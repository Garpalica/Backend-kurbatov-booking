from email import message

from django.http import response
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import render
import json

from django.views.decorators.csrf import csrf_exempt

room_db = {
    1: {"id": 1, "name": "Аудитория А-301", "capacity": 30, "is_booked": False},
    2: {"id": 2, "name": "Лекционный зал Б-102", "capacity": 120, "is_booked": True},
    3: {"id": 3, "name": "Компьютерный класс В-405", "capacity": 15, "is_booked": False}
}

next_id = 4

def health(request):
    return JsonResponse({'status': 'ok'}, status= 200)


def home(request):
    return HttpResponse("Все работает")


def check_field_types(data):
    if 'name' in data:
        if not isinstance(data['name'],str) or data['name'].strip() == "":
            return False, {'error': 'Поле name должно быть не пустым', 'field': 'name'}
    if 'capacity' in data:
        if not isinstance(data['capacity'], int) or data['capacity'] < 0:
            return False, {'error': 'Поле capacity должно быть положительным не нелувым целым числом', 'field': 'capacity'}
    if 'is_booked' in data:
        if not isinstance(data['is_booked'], bool):
            return False, {'error': 'Поле is_booked должно быть булевым', 'field': 'is_booked'}
    return True, None

def is_valid_post(data):
    allowed_fields = ['name', 'capacity', 'is_booked']

    for key in data.keys():
        if key not in allowed_fields:
            return False, {"error": f"Неизвестное поле: {key}", "field": key}

    if 'name' not in data:
        return False, {"error": "Поле 'name' обязательно", "field": "name"}
    return check_field_types(data)


def is_valid_patch(data):
    allowed_fields = ['name', 'capacity', 'is_booked']

    for key in data.keys():
        if key not in allowed_fields:
            return False, {"error": f"Неизвестное поле: {key}", "field": key}
    return check_field_types(data)


def get_json(request):
    if request.content_type == 'application/json':
        try:
            body_bytes = request.body
            data = json.loads(body_bytes)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Неверный формат JSON", "field": "body"}, status=400)
        return data
    else:
        return JsonResponse({"error": "Ожидался формат application/json"}, status=400)


@csrf_exempt
def rooms(request, id=None):
    if request.method == 'GET' and id is None:
        limit_str = request.GET.get('limit', '10')
        offset_str = request.GET.get('offset', '0')
        name_param = request.GET.get('name')
        capacity_param = request.GET.get('capacity')
        booked_param = request.GET.get('is_booked')

        try:
            limit = int(limit_str)
            offset = int(offset_str)
            if limit < 0 or offset < 0:
                return JsonResponse({'error': 'limit и offset не могут быть отрицательными', 'field': 'queryparam'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'limit и offset должны быть целым числом', 'field': 'queryparam'}, status=400)
        all_room = list(room_db.values())

        if name_param:
            if not isinstance(name_param, str):
                return JsonResponse({'error': 'name должен быть строковым', 'field': 'queryparam'}, status=400)
            all_room = [room for room in all_room if room['name'] == name_param]
        if capacity_param:
            try:
                capacity = int(capacity_param)
                if capacity < 0:
                    return JsonResponse({'error': 'capacity не может быть отрицательными', 'field': 'queryparam'}, status=400)
                all_room = [room for room in all_room if room['capacity'] == capacity]
            except ValueError:
                return JsonResponse({'error': 'capacity должны быть целым числом', 'field': 'queryparam'}, status=400)
        if booked_param:
            if booked_param == 'true':
                book_val = True
            elif booked_param == 'false':
                book_val = False
            else:
                return JsonResponse({'error': 'is_booking должно быть булевым', 'field': 'queryparam'}, status=400)
            all_room = [room for room in all_room if room['is_booked'] == book_val]

        count_rooms = len(all_room)
        paginated_room = all_room[offset:offset + limit]
        return JsonResponse({
            'offset': offset,
            'limit': limit,
            'total': count_rooms,
            'rooms': paginated_room
        }, status=200)
    elif request.method == 'GET' and id is not None:
        if id not in room_db:
            return JsonResponse({'error': "Записи с таким id не существует", "field": "id"}, status=404)
        room_id  = room_db[id]
        return JsonResponse(room_id, status=200)
    elif request.method == 'POST':
        data = get_json(request)
        if not isinstance(data, dict):
            return data
        is_valid, error_response = is_valid_post(data)
        if is_valid:
            global next_id
            new_room = {
                'id': next_id,
                "name": data['name'],
                "capacity": data.get('capacity', 0),
                "is_booked": data.get('is_booked', False)
            }
            room_db[next_id] = new_room
            next_id += 1
            return JsonResponse(new_room, status=201)
        else:
            return JsonResponse(error_response, status=400)

    elif request.method == 'PATCH' and id is not None:
        data = get_json(request)
        if not isinstance(data, dict):
            return data
        if id not in room_db:
            return JsonResponse({'error': "Записи с таким id не существует", "field": "id"}, status=404)
        is_valid, error_response = is_valid_patch(data)
        if is_valid:
            updates_room = room_db[id]
            for key, value in data.items():
                updates_room[key] = value
            return JsonResponse(updates_room,status=200)
        else:
            return JsonResponse(error_response, status=400)
    elif request.method == "DELETE":
        if id not in room_db:
            return JsonResponse({'error': 'Нет комнаты с таким id', 'field': 'id'}, status=404)
        del room_db[id]
        return HttpResponse(status=204)







