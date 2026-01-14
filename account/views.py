from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db.models import Q
from django.contrib import messages
from validate_email import validate_email
from account.mixing import LoginRequiredMixin, LogoutRequiredMixin
from account.forms import SignUpForm, SignInForm, ChangePasswordForm, ResetPasswordForm
from account.utilities import account_activation_token, ActivationEmailSender
import json
import logging


User = get_user_model()

logger = logging.getLogger('project')


# Username Validation
@method_decorator(never_cache, name='dispatch')
class UsernameValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username', '').strip()

        if not username:
            return JsonResponse({'status': 'error', 'message': 'Username cannot be empty'})

        if not username.isalnum():
            return JsonResponse({'status': 'error', 'message': 'Username should only contain letters and numbers'})

        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse(
                {'status': 'error', 'message': 'This username is already taken'})

        return JsonResponse(
            {'status': 'success', 'message': 'Username is valid and available'})


# Email Validation
@method_decorator(never_cache, name='dispatch')
class EmailValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()

        if not email:
            return JsonResponse(
                {'status': 'error', 'message': 'Email cannot be empty'})

        if not validate_email(email):
            return JsonResponse(
                {'status': 'error', 'message': 'Email is not valid'})

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse(
                {'status': 'error', 'message': 'This email is already in use'})

        return JsonResponse(
            {'status': 'success', 'message': 'Email is valid and available'})


# Password Validation
@method_decorator(never_cache, name='dispatch')
class PasswordValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        password = data.get('password', '')
        password2 = data.get('password2', '')

        if password != password2:
            return JsonResponse(
                {'status': 'error', 'message': 'Passwords do not match'})

        if len(password) < 8:
            return JsonResponse(
                {'status': 'error', 'message': 'Password must be at least 8 characters long'})

        return JsonResponse(
            {'status': 'success', 'message': 'Passwords match'})


# Sign In Validation
@method_decorator(never_cache, name='dispatch')
class SignInValidationView(generic.View):
    def post(self, request):
        data = json.loads(request.body)
        username_or_email = data.get('username', '').strip()

        if not username_or_email:
            return JsonResponse(
                {'status': 'error', 'message': 'Username or email is required'})

        if not User.objects.filter(
            Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)
        ).exists():
            return JsonResponse(
                {'status': 'error', 'message': 'No account found with this username or email'})

        return JsonResponse(
            {'status': 'success', 'message': 'Account exists'})


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
            messages.success(request, 'Account created. Check your email to activate your account via the link sent.')
            return redirect('sign-in')

        messages.error(request, 'Correct the errors below.')
        return render(request, 'account/sign-up.html', {'form': form})


# Sign In View
@method_decorator(never_cache, name='dispatch')
class SignInView(generic.View):
    def get(self, request):
        form = SignInForm()
        return render(request, 'account/sign-in.html', {'form': form})

    def post(self, request):
        form = SignInForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Your account is not activated yet.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, 'account/sign-in.html', {'form': form})

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
        form = ChangePasswordForm(user=request.user)
        return render(request, 'account/changes-password.html', {'form': form})

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            new_password = form.cleaned_data.get('password')
            
            # Update user password
            request.user.set_password(new_password)
            request.user.save()
            
            # Update session so user doesn't get logged out immediately
            update_session_auth_hash(request, request.user)
            
            messages.success(request, "Password successfully changed!")
            
            # logout user after password change
            logout(request)
            return redirect('sign-in')  

        return render(request, 'account/changes-password.html', {'form': form})

# Reset Password View
class ResetPasswordView(generic.View):
    def get(self, request):
        form = ResetPasswordForm()
        return render(request, 'account/reset-password.html', {'form': form})