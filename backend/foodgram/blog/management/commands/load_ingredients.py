import csv

from django.core.management.base import BaseCommand

from blog.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из CSV'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Путь к CSV-файлу')

    def handle(self, *args, **options):
        with open(options['path'], encoding='utf-8') as f:
            reader = csv.reader(f)
            ingredients = []
            for row in reader:
                if len(row) < 2:
                    continue
                name = ' '.join(','.join(row[:-1]).split())
                unit = row[-1].strip()
                ingredients.append(Ingredient(name=name, measurement_unit=unit))
        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Загружено: {len(ingredients)}'))
