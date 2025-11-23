from django.shortcuts import redirect
from django.urls import reverse_lazy

class LoginRequiredMixin:
    """
    Mixin to ensure the user is authenticated.
    Redirects to the given URL if not authenticated.
    """
    login_url = reverse_lazy('home')  # default redirect URL

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class LogoutRequiredMixin:
    """
    Mixin to ensure the user is NOT authenticated.
    Redirects to the given URL if already authenticated.
    """
    redirect_authenticated_url = reverse_lazy('sign-in')  # default redirect URL

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.redirect_authenticated_url)
        return super().dispatch(request, *args, **kwargs)
