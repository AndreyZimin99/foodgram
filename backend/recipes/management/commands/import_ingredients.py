# import json
# from django.core.management.base import BaseCommand
# from recipes.models import Ingredient


# class Command(BaseCommand):
#     help = 'Импортировать ингредиенты из JSON файла'

#     def add_arguments(self, parser):
#         parser.add_argument('/data/ingredients.json',
#                             type=str, help='Путь к JSON файлу')

#     def handle(self, *args, **kwargs):
#         file_path = kwargs['/data/ingredients.json']
#         try:
#             with open(file_path) as f:
#                 data = json.load(f)
#                 for item in data:
#                     ingredient = Ingredient(**item)
#                     ingredient.save()
#                     self.stdout.write(
#                         self.style.SUCCESS(f'Успешно добавлено: {item}'))
#         except Exception as e:
#             self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))


import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import os


class Command(BaseCommand):
    help = 'Импортировать ингредиенты из JSON файла'

    JSON_FILE_PATH = os.path.join('data', 'ingredients.json')

    def handle(self, *args, **kwargs):
        try:
            with open(self.JSON_FILE_PATH) as f:
                data = json.load(f)
                for item in data:
                    ingredient = Ingredient(**item)
                    ingredient.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Успешно добавлено: {item}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
