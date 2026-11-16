import os

from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone
from booking.settings import SECRET_KEY
from lab2.validations import ValidationError
import jwt

class UserModelsMixin:
    def create_user(self, **kwargs):
        User = get_user_model()
        if User.objects.filter(username=kwargs['username']).exists():
            raise ValidationError(f'Пользователь с именем {kwargs["username"]} уже существует, выберите другое имя', field='username')
        new_user = User()
        new_user.username = kwargs['username']
        new_user.set_password(kwargs['password'])
        new_user.save()
        return new_user

def create_token(user):
    JWT_SECRET = SECRET_KEY
    payload = {
        'user_id': user.pk,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv('TIME_ALIVE'))),
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token


