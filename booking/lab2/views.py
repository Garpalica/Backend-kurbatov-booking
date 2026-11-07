from email import message
from gc import get_objects

from django.db.models.enums import ChoicesType
from django.http import response
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
import json
from datetime import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from psycopg2._psycopg import DatabaseError

from lab2.models import Rooms, Bookings
from .validations import (
    BadRequestError,
    ValidationError,
    is_valid_fields_post,
    is_valid_fields_patch
)

def get_json(request):
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            raise BadRequestError("Неверный формат JSON")
        return data
    else:
        raise BadRequestError("Ожидался формат application/json")

def patch_room(new_room, data):
    if 'name' in data:
        if Rooms.objects.filter(name=data['name']).exclude(pk=new_room.pk).exists():
            raise ValidationError(f'Комната с таким name: {data["name"]} уже существует выберите другое name', field= 'name')
        new_room.name = data['name']
    if 'capacity' in data:
        new_room.capacity = data['capacity']
    if 'is_booked' in data:
        new_room.is_booked = data['is_booked']
    new_room.save()

def parsing_query_param(request):
    limit_param = request.GET.get('limit', 10)
    offset_param = request.GET.get('offset', 0)
    name_param = request.GET.get('name', False)
    capacity_param= request.GET.get('capacity', False)
    is_booked_param = request.GET.get('is_booked', False)
    clear_param = {}
    if name_param:
        if name_param.strip() == "":
            raise ValidationError('Параметр name должен быть не пустой строкой', field='name')
        clear_param['name'] = name_param
    if capacity_param:
        try:
            capacity = int(capacity_param)
            if capacity >= 100 or capacity <= 0:
                raise ValidationError('Параметр capacity должен быть >0 и <100', field='queryparam')
            clear_param['capacity'] = capacity
        except ValueError:
            raise ValidationError('Параметр capacity должен быть целым числом', field='queryparam')
    if is_booked_param:
        try:
            is_booked = int(is_booked_param)
            if is_booked not in (0,1):
                raise ValidationError('Параметр is_booked должен быть либо 1, либо 0', field='queryparam')
            clear_param['is_booked'] = is_booked
        except ValueError:
            raise ValidationError('Параметр is_booked должен быть целым числом', field='queryparam')
    try:
        limit = int(limit_param)
        offset = int(offset_param)
        if limit < 0 or offset < 0:
            raise ValidationError('Параметры limit и offset должны быть не отрицательными', field='queryparam')
        clear_param['limit'] = limit
        clear_param['offset'] = offset
    except ValueError:
        raise ValidationError('Параметры limit и offset должны быть целыми числами', field='queryparam')

    return clear_param



def health(request):
    return JsonResponse({'status': 'ok'}, status=200)


@csrf_exempt
def rooms(request, id=None):
    if request.method == "GET" and id is None:
        all_rooms = Rooms.objects.all()
        try:
            query = parsing_query_param(request)
        except ValidationError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)

        if 'name' in query:
            all_rooms = all_rooms.filter(name__icontains=query['name'])
        if 'capacity' in query:
            all_rooms = all_rooms.filter(capacity=query['capacity'])
        if 'is_booked' in query:
            all_rooms = all_rooms.filter(is_booked=query['is_booked'])
        limit = query['limit']
        offset = query['offset']
        total = all_rooms.count()
        paginated_rooms = all_rooms[offset: offset + limit]
        res = list(paginated_rooms.values('id', 'name','capacity', 'is_booked'))
        return JsonResponse({
            'offset': offset,
            'limit': limit,
            'total': total,
            'rooms': res
        }, status=200)
    elif request.method == "GET" and id is not None:
        try:
            room = Rooms.objects.get(pk=id)
        except Rooms.DoesNotExist:
            return JsonResponse({'error': f'Комнаты с id: {id} не найдено', 'field': 'id'}, status=404)
        res = {
            'id': room.id,
            'name': room.name,
            'capacity': room.capacity,
            'is_booked': room.is_booked
        }
        return JsonResponse(res, status=200)
    elif request.method == "POST" and id is None:
        try:
            data = get_json(request)
            is_valid_fields_post(data)
            if Rooms.objects.filter(name=data['name']).exists():
                return JsonResponse({'error': f'Комната с таким name: {data["name"]} уже существует', 'field': 'name'}, status=400)
            new_room = Rooms.objects.create(
                name=data['name'],
                capacity=data['capacity'],
                is_booked=data.get('is_booked', Rooms.Status.FREE)
            )
        except ValidationError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except BadRequestError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except DatabaseError:
            return JsonResponse({'error': "Произошла неизвестная ошибка на стороне bd", 'field': 'bd'}, status=500)
        res = {
            'id': new_room.id,
            'name': new_room.name,
            'capacity': new_room.capacity,
            'is_booked': new_room.is_booked
        }
        return JsonResponse(res,status=201)
    elif request.method == "PATCH" and id is not None:
        try:
            data = get_json(request)
            is_valid_fields_patch(data)
            try:
                new_room = Rooms.objects.get(pk=id)
            except Rooms.DoesNotExist:
                return JsonResponse({'error': f'Комнаты с id: {id} не найдено', 'field': 'id'}, status=404)
            patch_room(new_room, data)
        except ValidationError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except BadRequestError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except DatabaseError:
            return JsonResponse({'error': "Произошла неизвестная ошибка на стороне bd", 'field': 'bd'}, status=500)
        res = {
            'id': new_room.id,
            'name': new_room.name,
            'capacity': new_room.capacity,
            'is_booked': new_room.is_booked
        }
        return JsonResponse(res,status=200)
    elif request.method == "DELETE" and id is not None:
        if not (Rooms.objects.filter(pk=id).exists()):
            return JsonResponse({'error': f'Комнаты с таким id: {id} не существует', 'field': 'id'}, status=404)
        try:
            Rooms.objects.filter(pk=id).delete()
        except DatabaseError:
            return JsonResponse({'error': "Произошла неизвестная ошибка на стороне bd", 'field': 'bd'}, status=500)
        return HttpResponse(status=204)


@csrf_exempt
def bookings(request, room_id):
    if request.method == "GET":
        room = Rooms.objects.get(pk=room_id)




