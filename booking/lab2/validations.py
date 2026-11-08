from datetime import datetime
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from lab2.models import Rooms


class BadRequestError(Exception):
    def __init__(self, message, field='body'):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ValidationError(BadRequestError):
    pass

def is_valid_fields_post(data):
    allowed_fields = {'name', 'capacity', 'is_booked'}

    if 'name' not in data or 'capacity' not in data:
        raise ValidationError('Поля name и capacity обязательны для создания комнаты', field  = 'name,capacity')

    for key in data.keys():
        if key not in allowed_fields:
            raise ValidationError(f'Неизвестное поле {key}', field=key)
    return is_valid_param(data)

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

def is_valid_fields_patch(data):
    allowed_fields = {'name', 'capacity', 'is_booked'}

    for key in data.keys():
        if key not in allowed_fields:
            raise ValidationError(f'Неизвестное поле {key}', field=key)
    return is_valid_param(data)

def is_valid_param_bookings(data):
    start_str = data.get('start_datetime')
    start_dt = parse_datetime(start_str)
    end_str = data.get('end_datetime')
    end_dt = parse_datetime(end_str)

    if start_dt is None:
        raise ValidationError('Неверный формат даты. Ожидается ISO 8601', field='start_datetime')
    if not timezone.is_aware(start_dt):
        raise ValidationError('Присланный формат start_datetime должен содержать time_zone',  field='start_datetime')
    if end_dt is None:
        raise ValidationError('Неверный формат даты. Ожидается ISO 8601', field='end_datetime')
    if not timezone.is_aware(end_dt):
        raise ValidationError('Присланный формат end_datetime должен содержать time_zone',  field='end_datetime')
    if end_dt <= start_dt:
        raise ValidationError('Конец бронирование не может быть раньше чем его начало',  field='end_datetime')
    return start_dt,end_dt





def is_valid_field_bookings(data):
    allowed_fields = {'start_datetime', 'end_datetime'}

    if 'start_datetime' not in data or 'end_datetime' not in data:
        raise ValidationError('Поля start_datetime, end_datetime обязательны для создания новой брони')

    for key in data.keys():
        if key not in allowed_fields:
            raise ValidationError(f'Неизвестное поле: {key}', field=key)
    return is_valid_param_bookings(data)

