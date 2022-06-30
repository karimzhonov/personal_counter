"""python manage.py runccompare - Run schedules"""
from django.core.management.base import BaseCommand
from compare_face.__main__ import start


class Command(BaseCommand):
    def handle(self, *args, **options):
        start()
