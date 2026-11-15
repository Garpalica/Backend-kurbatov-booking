from email import message
from gc import get_objects


from django.db.models import Q, Avg
from django.db.models.aggregates import Sum, Count
from django.db.models.deletion import ProtectedError
from django.db.models.enums import ChoicesType
from django.http import response
from django.db import transaction
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
import json
from datetime import datetime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from psycopg2._psycopg import DatabaseError
from zoneinfo import ZoneInfo
from lab2.models import Rooms, Bookings
from .validations import (
    BadRequestError,
    ValidationError,
    is_valid_fields_post,
    is_valid_fields_patch, is_valid_field_bookings, get_json
)

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
    user = request.user

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
        res = list(paginated_rooms.values('id', 'name','capacity', 'is_booked', 'owner__username'))
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
            'is_booked': room.is_booked,
            'owner': room.owner.username
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
                is_booked=data.get('is_booked', Rooms.Status.FREE),
                owner=user
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
            'is_booked': new_room.is_booked,
            'owner': new_room.owner.username
        }
        return JsonResponse(res,status=201)
    elif request.method == "PATCH" and id is not None:
        try:
            data = get_json(request)
            is_valid_fields_patch(data)
            try:
                new_room = Rooms.objects.get(pk=id)
                if user.pk != new_room.owner_id:
                    return JsonResponse({'error': 'Запись может быть изменена только создателем', 'field': 'owner'}, status=403)
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
            'is_booked': new_room.is_booked,
            'owner': new_room.owner.username
        }
        return JsonResponse(res,status=200)
    elif request.method == "DELETE" and id is not None:
        if not (Rooms.objects.filter(pk=id).exists()):
            return JsonResponse({'error': f'Комнаты с таким id: {id} не существует', 'field': 'id'}, status=404)
        try:
            if user.pk != Rooms.objects.get(pk=id).owner_id:
                return JsonResponse({'error': 'Запись может быть удалена только создателем', 'field': 'owner'},status=403)
            Rooms.objects.filter(pk=id).delete()
        except ProtectedError:
            return JsonResponse({'error': "Комнату нельзя удалить, так как на нее есть запланированные встречи", 'field': 'bd'}, status=409)
        except DatabaseError:
            return JsonResponse({'error': "Произошла неизвестная ошибка на стороне bd", 'field': 'bd'}, status=500)
        return HttpResponse(status=204)


@csrf_exempt
def bookings(request, room_id):
    if room_id <= 0:
        return JsonResponse({'error': 'Поле room_id должно быть целым числом > 0', 'field': 'room_id' },status=400)
    if request.method == "GET":
        try:
            bookings_rooms = Rooms.objects.get(pk=room_id).bookings.all()
        except Rooms.DoesNotExist:
            return JsonResponse({'error': f'Комнаты с таким id: {room_id} не существует', 'field': 'room_id'}, status=400)

        tz = request.GET.get('tz', 'UTC')
        try:
            local_tz = ZoneInfo(tz)
        except Exception:
            return JsonResponse({'error': f'Зоны с названием: {tz} не существует', 'field': 'tz'}, status=400)
        res = []
        for booking in bookings_rooms:
            local_start = booking.start_datetime.astimezone(local_tz)
            local_end = booking.end_datetime.astimezone(local_tz)

            res.append({
                'id': booking.id,
                'start_datetime': local_start.isoformat(),
                'end_datetime': local_end.isoformat()
            })
        return JsonResponse(res, safe=False, status=200)

    elif request.method == "POST":
        try:
            data = get_json(request)
            start_time,end_time = is_valid_field_bookings(data)
        except ValidationError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)
        except BadRequestError as e:
            return JsonResponse({'error': e.message, 'field': e.field}, status=400)

        try:
            with transaction.atomic():

                room = Rooms.objects.select_for_update().get(pk=room_id)

                conflict = room.bookings.filter(
                    Q(start_datetime__lt=end_time) & Q(end_datetime__gt=start_time)
                ).exists()

                if conflict:
                    return JsonResponse({'error': 'На это время комната уже забронирована','field': 'start_datetime'}, status=409)

                new_booking = Bookings.objects.create(
                    start_datetime=start_time,
                    end_datetime=end_time,
                    room=room
                )

                room.is_booked = 1
                room.save()
            return JsonResponse({
                'id': new_booking.id,
                'start_datetime': start_time,
                'end_datetime': end_time,
                'room_id': room_id
            }, status=201)

        except Rooms.DoesNotExist:
            return JsonResponse({'error': f'Комнаты с таким id: {room_id} не существует', 'field': 'room_id'},status=400)
        except DatabaseError:
            return JsonResponse({'error': "Произошла неизвестная ошибка на стороне bd", 'field': 'bd'}, status=500)


def stats(request):
    res = {
        'Количество комнат': Rooms.objects.count(),
        'Средняя вместимость комнат': Rooms.objects.aggregate(avg=Avg('capacity'))['avg'],
        'Общая вместимость всех комнат': Rooms.objects.aggregate(sum=Sum('capacity'))['sum'],
        'Количество броней на каждую комнату': list(Bookings.objects.values('room_id').annotate(count=Count('id')))
    }
    return JsonResponse(res, status=200)








