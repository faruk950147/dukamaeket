from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.contrib import messages
from validate_email import validate_email
from account.mixing import LoginRequiredMixin, LogoutRequiredMixin
from account.forms import SignUpForm, SignInForm, ResetPasswordForm
from account.utilities import account_activation_token, ActivationEmailSender
import json
import logging


User = get_user_model()

logger = logging.getLogger('project')

import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError

User = get_user_model()

import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q

User = get_user_model()


# Username Validation
@method_decorator(never_cache, name='dispatch')
class UsernameValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username', '').strip()

        if not username:
            return JsonResponse({'error': 'Username cannot be empty'})

        if not username.isalnum():
            return JsonResponse({'error': 'Username should only contain alphanumeric characters'})

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'This username is already taken'})

        return JsonResponse({'valid': 'Username is valid and available'})


# Email Validation
@method_decorator(never_cache, name='dispatch')
class EmailValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email', '').strip()

        if not email:
            return JsonResponse({'error': 'Email cannot be empty'})

        if not validate_email(email):
            return JsonResponse({'error': 'Email is not valid'})

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'error': 'This email is already in use'})

        return JsonResponse({'valid': 'Email is valid and available'})


# Password Validation
@method_decorator(never_cache, name='dispatch')
class PasswordValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        password = data.get('password', '').strip()
        password2 = data.get('password2', '').strip()

        if password != password2:
            return JsonResponse({'error': 'Passwords do not match'})

        if len(password) < 8:
            return JsonResponse({'error': 'Your password is too short! Minimum 8 characters required.'})

        return JsonResponse({'valid': 'Password is valid'})


# SignIn Validation
@method_decorator(never_cache, name='dispatch')
class SignInValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username', '').strip()

        if not User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).exists():
            return JsonResponse({'username_error': 'No account found with this username or email. Please try again.'})

        return JsonResponse({'username_valid': True})


# Account Activation View
@method_decorator(never_cache, name='dispatch')
class AccountActivationView(generic.View):
    def get(self, request, uidb64, token):
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = User.objects.get(id=uid)
        if account_activation_token.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                messages.success(request, 'Account activated successfully.')
            else:
                messages.info(request, 'Account already activated.')
        else:
            messages.error(request, 'Activation link is invalid or expired.')
    
        return redirect('sign-in')


# Sign Up View
@method_decorator(never_cache, name='dispatch')
class SignUpView(generic.View):
    def get(self, request):
        return render(request, 'account/sign-up.html', {'form': SignUpForm()})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            # Send activation email
            ActivationEmailSender(user, request).send()
            messages.success(request, 'Account created. Check email to activate.')
            return redirect('sign-in')

        messages.error(request, 'Correct the errors below.')
        return render(request, 'account/sign-up.html', {'form': form})


# Sign In View
@method_decorator(never_cache, name='dispatch')
class SignInView(generic.View):
    def get(self, request):
        return render(request, 'account/sign-in.html', {'form': SignInForm()})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            messages.error(request, 'Activate your account first.')
        else:
            messages.error(request, 'Invalid username or password.')

        return redirect('sign-in')


# Sign Out View
@method_decorator(never_cache, name='dispatch')
class SignOutView(LoginRequiredMixin, generic.View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Signed out successfully.')
        return redirect('sign-in')


# Change Password View
@method_decorator(never_cache, name='dispatch')
class ChangesPasswordView(LoginRequiredMixin, generic.View):
    def get(self, request):
        return render(request, 'account/changes-password.html')

    def post(self, request):
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        if not request.user.check_password(current):
            messages.error(request, 'Current password incorrect')
            return redirect('change-password')

        if new != confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('change-password')

        if len(new) < 8:
            messages.error(request, 'Password too short')
            return redirect('change-password')

        request.user.set_password(new)
        request.user.save()
        logout(request)
        messages.success(request, 'Password changed. Login again.')
        return redirect('sign-in')