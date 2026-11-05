from django.db import models
from django.db.models import Q
from django.db.models.deletion import PROTECT


class Rooms(models.Model):
    class Status(models.IntegerChoices):
        FREE = 0, 'Свободно'
        BOOKED = 1, 'Забронировано'
    name = models.CharField(max_length=100, null=False)
    capacity = models.IntegerField(null=False)
    is_booked = models.IntegerField(choices=Status.choices, default=Status.FREE)

    class Meta:
        constraints = [models.CheckConstraint(
            name='capacity_gt_0',
            condition=Q(capacity__gt=0) & Q(capacity__lt=100),
            violation_error_message='Поле capacity должно быть больше нуля и меньше ста'
        )]
    def __str__(self):
        return self.name

class Bookings(models.Model):
    room = models.ForeignKey(Rooms, on_delete=PROTECT)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'Бронь на {self.room.name}'


