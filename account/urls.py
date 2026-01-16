from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from account.views import (
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
    ResetPasswordConfirmView,  
    UserInfoEditView,
    ShippingAddressView,
    ShippingAddressListView,
    AccountView
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

    # Reset password flow
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset_password_confirm'),
    
    path('user-info-edit/', UserInfoEditView.as_view(), name='user-info-edit'),
    path('shipping-address/', ShippingAddressView.as_view(), name='shipping-address'),
    path('address-list/', ShippingAddressListView.as_view(), name='address-list'),
    path('account/', AccountView.as_view(), name='account'),
]
