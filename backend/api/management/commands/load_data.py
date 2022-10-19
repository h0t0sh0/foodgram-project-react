import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    help = 'Load data dump'

    def add_arguments(self, parser):
        parser.add_argument('--ingredients', action='store_true', required=False)
        parser.add_argument('--tags', action='store_true', required=False)
        parser.add_argument('datafile', help='full filename path', default=None, type=str)

    def handle(self, *args, **kwargs):
        try:
            with open(kwargs['datafile'], encoding='utf-8') as fname:
                data = json.load(fname)
            if kwargs['ingredients']:
                for ingredient in data:
                    Ingredient.objects.create(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
            elif kwargs['tags']:
                for tag in data:
                    Tag.objects.create(
                        name=tag['name'],
                        color=tag['color'],
                        slug=tag['slug']
                    )
        except Exception as ex:
            raise CommandError(f'Error while load data: {ex}')
