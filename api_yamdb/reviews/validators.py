from datetime import date

from django.core.exceptions import ValidationError


def validate_year(val):
    current_year = date.today().year
    if val > current_year:
        raise ValidationError('Год должен быть меньше или равен текущему')
