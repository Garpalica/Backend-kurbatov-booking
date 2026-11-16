from datetime import datetime, timedelta, timezone
import os

from django.contrib.auth import authenticate
from django.http.response import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
import json
import jwt
from django.views.decorators.csrf import csrf_exempt

from booking.settings import SECRET_KEY
from lab2.validations import get_json, BadRequestError, ValidationError
from lab3.servises import UserModelsMixin, create_token
from lab3.validations import register_allow_fields, register_validation, login_allow_fields


@method_decorator(csrf_exempt, name='dispatch')
class RegisterUser(UserModelsMixin,View):
    def post(self, request):
        try:
            data = get_json(request)
            username, password = register_allow_fields(data)
            new_user = self.create_user(username=username, password=password)
        except ValidationError as e:
            if e.message.startswith('Пользователь с именем '):
                return JsonResponse({'error': e.message, 'field': e.field}, status=409)
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except BadRequestError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        return JsonResponse({
            'message': 'Пользователь успешно создан',
            'user_id': new_user.id,
            'username': new_user.username
        }, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class AboutUser(View):
    def get(self, request):
        return JsonResponse({
            'user_id': request.user.id,
            'user_name': request.user.username
        }, status= 200)


@method_decorator(csrf_exempt, name='dispatch')
class LoginUserBearer(View):
    def post(self, request):
        try:
            body = get_json(request)
            username, password = login_allow_fields(body)
        except ValidationError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except BadRequestError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        user = authenticate(username=username,password=password)
        if not user:
            return JsonResponse({'error': 'Пользователь не зарегистрирован', 'field': 'auth'})
        token = create_token(user)
        return JsonResponse({
            'user_id': user.pk,
            'access_token': token
        }, status=200)

