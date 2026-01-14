from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from account.views import (
    PasswordValidationView,
    UsernameValidationView,
    EmailValidationView,   
    PasswordValidationView,
    SignInValidationView, 
    AccountActivationView,
    SignUpView,
    SignInView,
    SignOutView,
    ChangesPasswordView,
    ResetPasswordView,
)
urlpatterns = [
    path('validate-username/', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('validate-password/', csrf_exempt(PasswordValidationView.as_view()), name='validate-password'),
    path('validate-signin/', csrf_exempt(SignInValidationView.as_view()), name='validate-signin'),
    path('activate-account/<uidb64>/<token>/', AccountActivationView.as_view(), name='activate-account'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-out/', SignOutView.as_view(), name='sign-out'),
    path('change-password/', ChangesPasswordView.as_view(), name='change-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password')
]
