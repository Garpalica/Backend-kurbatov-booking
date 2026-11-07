from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone
import tzdata
from datetime import datetime, timedelta

from lab2.models import Rooms, Bookings

class Command(BaseCommand):
    help = 'Заполняет тестовыми данными Таблицы PostgreSQL'

    def handle(self, *args, **options):

        if Rooms.objects.exists() and Bookings.objects.exists():
            self.stdout.write(self.style.ERROR("В БД уже имеются стартовые значения, а именно в таблице Rooms и Bookings"))
            return
        elif Rooms.objects.exists():
            self.stdout.write(self.style.WARNING("В БД уже имеются стартовые значения, а именно в таблице Rooms, заполнение будет произведено для таблицы Bookings"))

            rooms = Rooms.objects.all()
            for idx, room in enumerate(rooms):
                Bookings.objects.create(
                    room=room,
                    start_datetime=timezone.now() + timedelta(days=idx),
                    end_datetime=timezone.now() + timedelta(days=idx, hours=idx)
                )
            self.stdout.write(self.style.SUCCESS("Таблица Bookings успешно заполнена тестовыми данными"))
            return
        else:
            room1 = Rooms.objects.create(
                name="D734",
                capacity="30",
                is_booked=Rooms.Status.FREE
            )
            room2 = Rooms.objects.create(
                name="E856",
                capacity="60",
                is_booked=Rooms.Status.FREE
            )
            Bookings.objects.create(
                room=room1,
                start_datetime=timezone.now() + timedelta(days=1),
                end_datetime=timezone.now() + timedelta(days=1, hours=2)
            )
            Bookings.objects.create(
                room=room2,
                start_datetime=timezone.now() + timedelta(days=2),
                end_datetime=timezone.now() + timedelta(days=2, hours=3)
            )
            self.stdout.write(self.style.SUCCESS("Таблицы Rooms и Bookings успешно заполнены тестовыми данными"))
