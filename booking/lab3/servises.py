from django.contrib.auth import get_user_model

from lab2.validations import ValidationError


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



