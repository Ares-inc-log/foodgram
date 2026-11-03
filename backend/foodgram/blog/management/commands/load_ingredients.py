import csv
import json

from django.core.management.base import BaseCommand

from blog.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из CSV или JSON"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Путь к CSV/JSON-файлу")

    def handle(self, *args, **options):
        path = options["path"]
        ingredients = []

        with open(path, encoding="utf-8") as f:
            if path.lower().endswith(".json"):
                for item in json.load(f):
                    name = " ".join(item["name"].split())
                    unit = item["measurement_unit"].strip()
                    ingredients.append(
                        Ingredient(name=name, measurement_unit=unit)
                    )
            else:
                for row in csv.reader(f):
                    if len(row) < 2:
                        continue
                    name = " ".join(",".join(row[:-1]).split())
                    unit = row[-1].strip()
                    ingredients.append(
                        Ingredient(name=name, measurement_unit=unit)
                    )

        Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
        self.stdout.write(
            self.style.SUCCESS(f"Загружено: {len(ingredients)}")
        )
