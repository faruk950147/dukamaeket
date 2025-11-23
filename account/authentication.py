from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Single query: filter by username/email
        user_qs = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username))
        # Get the first match safely
        user = user_qs.first()
        # Check password on the fetched user object
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        # Safe and efficient
        return User.objects.filter(id=user_id).first()
