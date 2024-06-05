from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):

    def _create_users(self):
        User.objects.create_superuser('ssv','25yashasvi11@gmail.com','errornotfound')
        User.objects.create_user('aunicorndev','aunicorndeveloper@gmail.com','errornotfound')

    def handle(self, *args, **options):
        self._create_users()