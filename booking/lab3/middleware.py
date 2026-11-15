import base64
import binascii

from django.contrib.auth import authenticate
from django.http.response import JsonResponse
from lab2.validations import ValidationError


class LoginUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allow_urls = ['/auth/me/']

        if request.path in allow_urls:
            try:
                data_auth = self.get_auth_data(request)
                username, password = self.decode(data_auth)
            except ValidationError as e:
                return JsonResponse({'error': e.message, 'field': e.field}, status=400)
            user = authenticate(request, username=username, password=password)
            if user:
                request.user = user
                return self.get_response(request)
            else:
                return JsonResponse({'error': 'Пользователь не авторизирован', 'field': 'auth'}, status=401)
        return self.get_response(request)

    @staticmethod
    def decode(data):
        try:
            decoded_str = base64.b64decode(data).decode('utf-8')
            username, password = decoded_str.split(':', 1)
        except (binascii.Error, ValueError):
            raise ValidationError('Были введены не валидные реквизиты', field='headers')
        return username, password

    @staticmethod
    def get_auth_data(request):
        data_auth_str = request.headers.get('Authorization', False)
        if data_auth_str:
            try:
                type_auth, requisites = data_auth_str.split()
            except ValueError:
                raise ValidationError('Заголовок с реквизитами был задан не верно, нужен только тип auth и реквизиты', field='headers')
            if type_auth != 'Basic':
                raise ValidationError('Ожидалась BasicAuth', field='headers')
            if requisites.strip() == '':
                raise ValidationError('Реквизиты должны быть заполнены', field='headers')
            return requisites
        else:
            raise ValidationError('Отсутствуют поле авторизации для пользователя', field='headers')





