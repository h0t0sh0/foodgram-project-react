import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Load ingredients dump'

    def add_arguments(self, parser):
        parser.add_argument('datafile', help='full filename path', default=None, type=str)

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs['datafile'], encoding='utf-8') as fname:
                data = json.load(fname)
            for ingredient in data:
                Ingredient.objects.create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit']
                )
        except Exception as ex:
            raise CommandError(f'Error while load data: {ex}')
