from django.contrib.auth.backends import ModelBackend
import re
from .models import MyUser

class MutiAccountLoginAuth(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        try:
            if re.match('^1\d{10}$',username):
                user=MyUser.objects.get(phone=username)
            else:
                user=MyUser.objects.get(username=username)
        except MyUser.DoesNotExist:
            user=None
        
        if user and user.check_password(password):
            return user