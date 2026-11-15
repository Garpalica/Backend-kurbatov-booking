

from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
import json

from django.views.decorators.csrf import csrf_exempt

from lab2.validations import get_json, BadRequestError, ValidationError
from lab3.servises import UserModelsMixin
from lab3.validations import register_allow_fields, register_validation

@method_decorator(csrf_exempt, name='dispatch')
class RegisterUser(UserModelsMixin,View):
    def post(self, request):
        try:
            data = get_json(request)
            username, password = register_allow_fields(data)
            new_user = self.create_user(username=username, password=password)
        except ValidationError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except BadRequestError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        return JsonResponse({
            'message': 'Пользователь успешно создан',
            'user_id': new_user.id,
            'username': new_user.username
        }, status=201)




