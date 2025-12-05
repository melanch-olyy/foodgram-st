import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из JSON файла'

    def handle(self, *args, **options):

        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.json')

        if not os.path.exists(file_path):
            file_path = os.path.join(
                settings.BASE_DIR, '..', 'data', 'ingredients.json'
            )
        if not os.path.exists(file_path):
            file_path = '/app/data/ingredients.json'

        if not os.path.exists(file_path):
            raise CommandError(f'Файл не найден. Проверен путь: {file_path}')

        self.stdout.write(f'Загрузка из файла: {file_path}')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ingredients_to_create = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                for item in data
            ]

            Ingredient.objects.bulk_create(
                ingredients_to_create, ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {len(ingredients_to_create)} ингредиентов'
                )
            )

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Ошибка: Невалидный JSON файл'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка: {e}'))
