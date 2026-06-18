from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


class EmailOrEmployeeCodeBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')
        try:
            user = User.objects.get(
                Q(email=username) | Q(employee_code=username),
                is_active=True,
            )
        except User.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
