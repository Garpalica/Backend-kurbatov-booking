from lab2.validations import ValidationError, BadRequestError


def register_validation(data):
    if not isinstance(data['username'], str) or data['username'].strip() == '':
        raise ValidationError('Поле username должно быть строковым и не пустым', field='username')
    if not isinstance(data['password1'], str) or data['password1'].strip() == '':
        raise ValidationError('Поле password1 должно быть строковым и не пустым',  field='password1')
    if not isinstance(data['password2'], str) or data['password2'].strip() == '':
        raise ValidationError('Поле password1 должно быть строковым и не пустым', field='password2')
    if data['password1'] != data['password2']:
        raise ValidationError('Подтверждение пароля не совпадет с указанным паролем', field='password2')
    return data['username'], data['password1']

def register_allow_fields(data):
    allow_fields = {'username', 'password1', 'password2'}

    for field in allow_fields:
        if field not in data:
            raise BadRequestError('Поля username, password1, password2 обязательны для регистрации')

    if allow_fields != set(data):
        raise BadRequestError('Указаны лишние поля')

    return register_validation(data)