from django.shortcuts import redirect, render
from django.views import generic
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import re
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from urllib3 import request
from account.mixing import LoginRequiredMixin, LogoutRequiredMixin
from account.forms import SignUpForm, SignInForm, ResetPasswordForm

User = get_user_model()


# UsernameValidationView
@method_decorator(never_cache, name='dispatch')
class UsernameValidationView(generic.View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()

            if not isinstance(username, str) or not username.isalnum():
                return JsonResponse({'username_error': 'Username should only contain alphanumeric characters'})

            if User.objects.filter(username=username).exists():
                return JsonResponse({'username_error': 'Sorry, this username is already taken. Choose another one.'})

            return JsonResponse({'username_valid': 'Username is available'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'})


# SignInValidationView
@method_decorator(never_cache, name='dispatch')
class SignInValidationView(generic.View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username', '').strip()
            if not User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).exists():
                return JsonResponse({'username_error': 'No account found with this username or email. Please try again.'}, status=404)
            return JsonResponse({'username_valid': True}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=404)

# SignUpView
@method_decorator(never_cache, name='dispatch')
class SignUpView(LogoutRequiredMixin, generic.View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'account/sign-up.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        try:
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                messages.success(request, 'Account created successfully. Please sign in.')
                return redirect('sign-in')
            else:
                return render(request, 'account/sign-up.html', {'form': form})
        except Exception as e:
            messages.error(request, 'An error occurred during sign up. Please try again.')
            return render(request, 'account/sign-up.html', {'form': form})

# SignInView     
@method_decorator(never_cache, name='dispatch')
class SignInView(LogoutRequiredMixin, generic.View):
    def get(self, request):
        form = SignInForm()
        return render(request, 'account/sign-in.html', {'form': form})

    def post(self, request):
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have signed in successfully.')
                return redirect('home')  
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        return render(request, 'account/sign-in.html', {'form': form})

# SignOutView     
@method_decorator(never_cache, name='dispatch')
class SignOutView(LoginRequiredMixin, generic.View):
    def get(self, request):
        try:
            logout(request)
            messages.success(request, 'You have been signed out successfully.')
            return redirect('sign-in')  
        except Exception as e:
            messages.error(request, 'An error occurred during sign out. Please try again.')
            return redirect('sign-in')  

# ChangesPasswordView
@method_decorator(never_cache, name='dispatch')
class ChangesPasswordView(LoginRequiredMixin, generic.View):
    def get(self, request):
        
        return render(request, 'account/changes-password.html')
    def post(self, request):
        try:
            pass
        except Exception as e:
            print(str(e))
        return render(request, 'account/changes-password.html')

# ResetPasswordView
@method_decorator(never_cache, name='dispatch')
class ResetPasswordView(LogoutRequiredMixin, generic.View):
    def get(self, request):
        return render(request, 'account/reset-password.htm')
    def post(self, request):
        try:
            pass
        except Exception as e:
            print(str(e))

        return render(request, 'account/reset-password.htm')  
    
# ResetPasswordConfirmView
@method_decorator(never_cache, name='dispatch')
class ResetPasswordConfirmView(LoginRequiredMixin, generic.View):
    def get(self, request):
        return render(request, 'account/reset-password.htm')
    def post(self, request):
        try:
            pass
        except Exception as e:
            print(str(e))
        return render(request, 'account/reset-password.htm')
    