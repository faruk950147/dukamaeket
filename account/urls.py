from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from account.views import (
    UsernameValidationView,
    EmailValidationView,   
    SignInValidationView, 
    SignUpView,
    SignInView,
    SignOutView,
    ChangesPasswordView,
    ResetPasswordView,
    ResetPasswordConfirmView
)
urlpatterns = [
    path('validate-username/', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email/', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
    path('validate-signin/', csrf_exempt(SignInValidationView.as_view()), name='validate-signin'),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-out/', SignOutView.as_view(), name='sign-out'),
    path('change-password/', ChangesPasswordView.as_view(), name='change-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
]
