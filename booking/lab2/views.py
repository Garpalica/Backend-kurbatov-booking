from email import message

from django.db.models.enums import ChoicesType
from django.http import response
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
import json
from lab2.models import Rooms





class BadRequestError(Exception):
    def __init__(self, message, field='body'):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ValidationError(BadRequestError):
    pass

def get_json(request):
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            raise BadRequestError("Неверный формат JSON")
        return data
    else:
        raise BadRequestError("Ожидался формат application/json")

def is_valid_param(data):
    if 'name' in data:
        if not isinstance(data['name'],str) or data['name'].strip() == "":
            raise ValidationError("Поле name должно быть не пустой строкой", field="name")
    if 'capacity' in data:
        if not (isinstance(data['capacity'], int) and 0 < data['capacity'] < 100):
            raise ValidationError("Поле capacity должно быть числом > 0 и < 100", field="capacity")
    if 'is_booked' in data:
        if not (isinstance(data['is_booked'], int) and data['is_booked'] in (Rooms.Status.FREE, Rooms.Status.BOOKED)):
            raise ValidationError("Поле is_booked должно быть бинарным", field="is_booked")
    return True


def is_valid_fields(data):
    allowed_fields = {'name', 'capacity', 'is_booked'}

    for key in data.keys():
        if key not in allowed_fields:
            raise ValidationError(f'Неизвестное поле {key}', field=key)
    return is_valid_param(data)


# def parsing_fields_json(data):




def health(request):
    return JsonResponse({'status': 'ok'}, status=200)



def rooms(request, id=None):
    if request.method == "GET" and id is None:
        rooms = list(Rooms.objects.values('id', 'name', 'capacity', 'is_booked'))
        return JsonResponse(rooms, safe=False ,status=200)
    # if request.method == "GET":
        # try:
        #     data = get_json(request)
        #     is_valid_fields(data)
        # except BadRequestError as e:
        #     return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        # except ValidationError as e:
        #     return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        #
        # room = get_object_or_404(pk=data[id])


