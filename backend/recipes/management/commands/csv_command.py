import os
import csv

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    """Загружает csv-данные в базу."""

    def handle(self, *args, **kwargs):
        call_command('migrate')
        with open(
            os.path.join(
                settings.BASE_DIR,
                'data/ingredients.csv'
            ), 'r', encoding='utf8'
        ) as file_scv:
            csv_reader = csv.DictReader(file_scv)
            Ingredient.objects.bulk_create(
                Ingredient(**data) for data in csv_reader
            )
