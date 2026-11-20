import base64
import binascii

import jwt
from django.contrib.auth import authenticate, get_user_model
from django.http.response import JsonResponse

from booking.settings import SECRET_KEY
from lab2.validations import ValidationError


class LoginUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allow_urls = ['/auth/me/']
        allow_method = {'POST', 'DELETE', 'PATCH'}
        user = None
        if request.path in allow_urls or (request.path.startswith('/db/api/') and request.method in allow_method):
            try:
                type_auth, data_auth = self.get_auth_data(request)
                if type_auth == 'Basic':
                    username, password = self.decode_basic(data_auth)
                    user = authenticate(request, username=username, password=password)
                elif type_auth == 'Bearer':
                    user_id= self.decode_bearer(data_auth)
                    user = get_user_model().objects.filter(pk=user_id).first()
            except ValidationError as e:
                return JsonResponse({'error': e.message, 'field': e.field}, status=401)
            if user:
                request.user = user
                return self.get_response(request)
            else:
                return JsonResponse({'error': 'Пользователь не авторизирован', 'field': 'auth'}, status=401)
        return self.get_response(request)

    @staticmethod
    def decode_basic(data):
        try:
            decoded_str = base64.b64decode(data).decode('utf-8')
            username, password = decoded_str.split(':', 1)
        except (binascii.Error, ValueError):
            raise ValidationError('Были введены не валидные реквизиты', field='headers')
        return username, password

    @staticmethod
    def decode_bearer(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload['user_id']
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise ValidationError('Неверный или просроченный токен', field='auth')

    @staticmethod
    def get_auth_data(request):
        data_auth_str = request.headers.get('Authorization', False)
        if data_auth_str:
            try:
                type_auth, requisites = data_auth_str.split()
            except ValueError:
                raise ValidationError('Заголовок с реквизитами был задан не верно, нужен только тип auth и реквизиты', field='headers')
            if type_auth != 'Basic' and type_auth != 'Bearer':
                raise ValidationError('Ожидалась BasicAuth or BearerAuth', field='headers')
            if requisites.strip() == '':
                raise ValidationError('Реквизиты должны быть заполнены', field='headers')
            return type_auth,requisites
        else:
            raise ValidationError('Отсутствуют поле авторизации для пользователя', field='headers')





