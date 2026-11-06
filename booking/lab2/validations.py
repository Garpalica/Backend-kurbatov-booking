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
