import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.is_active) + str(user.id) + str(timestamp)


account_activation_token = AppTokenGenerator()


class EmailThread(threading.Thread):
    def __init__(self, email):
        super().__init__()
        self.email = email

    def run(self):
        self.email.send(fail_silently=False)


class ActivationEmailSender:
    def __init__(self, user, request):
        self.user = user
        self.request = request

    def send(self):
        current_site = get_current_site(self.request)
        uid = urlsafe_base64_encode(force_bytes(self.user.id))
        token = account_activation_token.make_token(self.user)

        scheme = 'https' if self.request.is_secure() else 'http'
        path = reverse('activate-account', kwargs={'uidb64': uid, 'token': token})
        activation_url = f"{scheme}://{current_site.domain}{path}"

        subject = 'Activate your account'
        message = (
            f"Hello {self.user.username},\n\n"
            f"Click the link below to activate your account:\n\n"
            f"{activation_url}\n\n"
            f"Thank you."
        )

        email = EmailMessage(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email]
        )
        EmailThread(email).start()
