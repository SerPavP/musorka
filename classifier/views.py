import os
import re
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .ml_model import classify_waste

def index(request):
    """Главная страница"""
    context = {
        'title': 'Классификация отходов с использованием методов интеллектуального анализа данных',
        'subtitle': 'Электронное учебное пособие для студентов инженерных специальностей',
        'authors': 'Айдынқызы Айдана, Рахимжанова Ляззат Болтабаевна',
        'university': 'КазНУ имени аль-Фараби',
        'year': '2021',
    }
    return render(request, 'classifier/index.html', context)

def practice(request):
    """Страница практики машинного обучения - загрузка и классификация изображений"""
    result = None
    error = None
    uploaded_image_url = None
    
    if request.method == 'POST' and 'image' in request.FILES:
        try:
            uploaded_file = request.FILES['image']
            
            # Сохраняем файл
            file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            file_path = os.path.join(settings.MEDIA_ROOT, file_name)
            
            # Классифицируем изображение
            result = classify_waste(file_path)
            uploaded_image_url = f'/media/{file_name}'
            
            # Удаляем файл после обработки (опционально, можно оставить для отображения)
            # default_storage.delete(file_name)
            
        except Exception as e:
            error = f"Ошибка при обработке изображения: {str(e)}"
            if 'file_path' in locals() and os.path.exists(file_path):
                default_storage.delete(file_name)
    
    context = {
        'result': result,
        'error': error,
        'uploaded_image_url': uploaded_image_url,
    }
    return render(request, 'classifier/practice.html', context)

def theory(request):
    """Страница теории машинного обучения - показывает text.html с sidebar навигацией"""
    from .utils import FIXED_NAVIGATION_STRUCTURE
    
    html_file_path = os.path.join(settings.BASE_DIR, 'text.html')
    content = ""
    error_message = ""
    sections_content = {}
    
    if os.path.exists(html_file_path):
        try:
            # Читаем файл в UTF-8 (text.html использует UTF-8)
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Извлекаем содержимое из контейнера (div.container)
            if content:
                # Ищем div.container
                container_match = re.search(r'<div[^>]*class=["\']container["\'][^>]*>(.*?)</div>\s*</body>', content, re.DOTALL | re.IGNORECASE)
                if container_match:
                    content = container_match.group(1)
                    # Удаляем оглавление (toc), так как у нас есть sidebar навигация
                    content = re.sub(r'<div[^>]*class=["\']toc["\'][^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
                    # Удаляем hr после оглавления
                    content = re.sub(r'<hr[^>]*>', '', content, flags=re.IGNORECASE)
                    # Удаляем мета-информацию (название, авторы и т.д.) до первого h1
                    content = re.sub(r'<p>Название:.*?</p>', '', content, flags=re.DOTALL | re.IGNORECASE)
                    content = re.sub(r'<p>Электронное учебное пособие.*?</p>', '', content, flags=re.DOTALL | re.IGNORECASE)
                    content = re.sub(r'<p>Авторы:.*?</p>', '', content, flags=re.DOTALL | re.IGNORECASE)
                    content = re.sub(r'<p>Учебное заведение:.*?</p>', '', content, flags=re.DOTALL | re.IGNORECASE)
                    content = re.sub(r'<p>Год:.*?</p>', '', content, flags=re.DOTALL | re.IGNORECASE)
                else:
                    # Если не нашли container, извлекаем body
                    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
                    if body_match:
                        content = body_match.group(1)
                        # Удаляем оглавление
                        content = re.sub(r'<div[^>]*class=["\']toc["\'][^>]*>.*?</div>', '', content, flags=re.DOTALL | re.IGNORECASE)
                        content = re.sub(r'<hr[^>]*>', '', content, flags=re.IGNORECASE)
                
                # Разделяем контент по секциям
                for i, nav_item in enumerate(FIXED_NAVIGATION_STRUCTURE):
                    section_id = nav_item['id']
                    # Ищем начало секции по ID
                    pattern = rf'<h[12][^>]*id=["\']?{re.escape(section_id)}["\'][^>]*>.*?</h[12]>'
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    
                    if match:
                        start_pos = match.start()
                        # Ищем конец секции
                        end_pos = len(content)
                        
                        # Ищем следующую секцию того же или более высокого уровня
                        for j in range(i + 1, len(FIXED_NAVIGATION_STRUCTURE)):
                            next_item = FIXED_NAVIGATION_STRUCTURE[j]
                            next_id = next_item['id']
                            
                            # Для секций уровня 1 - ищем следующую секцию уровня 1
                            # Для секций уровня 2 - ищем следующую секцию уровня 2 того же родителя или следующую секцию уровня 1
                            if nav_item['level'] == 1:
                                if next_item['level'] == 1:
                                    next_pattern = rf'<h[12][^>]*id=["\']?{re.escape(next_id)}["\'][^>]*>'
                                    next_match = re.search(next_pattern, content[start_pos:], re.IGNORECASE)
                                    if next_match:
                                        end_pos = start_pos + next_match.start()
                                        break
                            else:  # level == 2
                                # Ищем следующую секцию уровня 2 того же родителя или следующую секцию уровня 1
                                if (next_item['level'] == 2 and next_item.get('parent') == nav_item.get('parent')) or next_item['level'] == 1:
                                    next_pattern = rf'<h[12][^>]*id=["\']?{re.escape(next_id)}["\'][^>]*>'
                                    next_match = re.search(next_pattern, content[start_pos:], re.IGNORECASE)
                                    if next_match:
                                        end_pos = start_pos + next_match.start()
                                        break
                        
                        section_content = content[start_pos:end_pos]
                        sections_content[section_id] = section_content
        except Exception as e:
            error_message = f"Ошибка чтения файла: {str(e)}"
    else:
        error_message = f"Файл text.html не найден в корне проекта: {settings.BASE_DIR}"
    
    context = {
        'html_content': content,
        'sections_content': sections_content,
        'error_message': error_message,
        'navigation': FIXED_NAVIGATION_STRUCTURE,
    }
    return render(request, 'classifier/theory.html', context)
