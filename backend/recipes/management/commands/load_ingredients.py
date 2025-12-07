import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов в базу данных'

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        potential_paths = [
            base_dir / 'data' / 'ingredients.json',
            base_dir.parent / 'data' / 'ingredients.json',
            Path('/app/data/ingredients.json'),
        ]

        target_file = None
        for path in potential_paths:
            if path.exists():
                target_file = path
                break

        if not target_file:
            raise CommandError('Файл ingredients.json не найден.')

        self.stdout.write(f'Чтение файла: {target_file}')

        try:
            with open(target_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            objs = [
                Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
                for item in data
            ]

            Ingredient.objects.bulk_create(objs, ignore_conflicts=True)
            self.stdout.write(
                self.style.SUCCESS(f'Добавлено: {len(objs)} ингредиентов.')
            )

        except Exception as error:
            raise CommandError(f'Ошибка импорта: {error}')
