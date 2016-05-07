from django.core.management.base import BaseCommand, CommandError
from apps.autenticacion.apps import AutenticacionConfig as x

class Command(BaseCommand):
    help = 'Populate database with default permissions'


    def handle(self, *args, **options):

        x.get_ready(x)
        self.stdout.write(self.style.SUCCESS('Successfully loaded permissions'))