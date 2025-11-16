"""
Команда для импорта теории из MHT или HTML файла в БД
Использование: python manage.py import_theory
"""
from django.core.management.base import BaseCommand
from classifier.utils import parse_html_to_sections


class Command(BaseCommand):
    help = 'Импортирует теорию из MHT или HTML файла в базу данных'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю импорт теории...')
        self.stdout.write('Ищу файлы: .mht или .htm')
        
        success, message = parse_html_to_sections()
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'OK: {message}'))
            self.stdout.write(self.style.SUCCESS('Теперь вы можете редактировать секции через админ-панель Django!'))
        else:
            self.stdout.write(self.style.ERROR(f'ERROR: {message}'))
            self.stdout.write(self.style.WARNING('Убедитесь, что файл "text.mht", "text.html" или файл с полным названием находится в корне проекта.'))

