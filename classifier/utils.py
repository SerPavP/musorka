"""
Утилиты для работы с теорией
"""

# Фиксированная структура навигации (не редактируется через админ)
FIXED_NAVIGATION_STRUCTURE = [
    {'id': 'intro', 'text': 'Введение', 'level': 1, 'order': 1},
    {'id': 'section1', 'text': '1. Общая характеристика отходов', 'level': 1, 'order': 2},
    {'id': 'section1-1', 'text': 'Определение отходов', 'level': 2, 'order': 3, 'parent': 'section1'},
    {'id': 'section1-2', 'text': 'Классификация отходов', 'level': 2, 'order': 4, 'parent': 'section1'},
    {'id': 'section1-3', 'text': 'Экологические последствия неправильной утилизации', 'level': 2, 'order': 5, 'parent': 'section1'},
    {'id': 'section1-4', 'text': 'Законодательство и стандарты по управлению отходами', 'level': 2, 'order': 6, 'parent': 'section1'},
    {'id': 'section2', 'text': '2. Основы машинного обучения', 'level': 1, 'order': 7},
    {'id': 'section2-1', 'text': 'Что такое машинное обучение (ML) и отличие от традиционного программирования', 'level': 2, 'order': 8, 'parent': 'section2'},
    {'id': 'section2-2', 'text': 'Основные задачи машинного обучения', 'level': 2, 'order': 9, 'parent': 'section2'},
    {'id': 'section2-3', 'text': 'Алгоритмы машинного обучения', 'level': 2, 'order': 10, 'parent': 'section2'},
    {'id': 'section2-4', 'text': 'Этапы работы с данными в ML', 'level': 2, 'order': 11, 'parent': 'section2'},
    {'id': 'section2-5', 'text': 'Метрики оценки моделей', 'level': 2, 'order': 12, 'parent': 'section2'},
    {'id': 'section3', 'text': '3. Интеллектуальный анализ данных (Data Mining)', 'level': 1, 'order': 13},
    {'id': 'section3-1', 'text': 'Определение Data Mining и отличие от машинного обучения', 'level': 2, 'order': 14, 'parent': 'section3'},
    {'id': 'section3-2', 'text': 'Методы анализа данных в Data Mining', 'level': 2, 'order': 15, 'parent': 'section3'},
    {'id': 'section3-3', 'text': 'Применение Data Mining к классификации отходов', 'level': 2, 'order': 16, 'parent': 'section3'},
    {'id': 'section3-4', 'text': 'Инструменты для Data Mining', 'level': 2, 'order': 17, 'parent': 'section3'},
    {'id': 'section4', 'text': '4. Практическая классификация отходов', 'level': 1, 'order': 18},
    {'id': 'section4-1', 'text': 'Источники данных', 'level': 2, 'order': 19, 'parent': 'section4'},
    {'id': 'section4-2', 'text': 'Предобработка данных', 'level': 2, 'order': 20, 'parent': 'section4'},
    {'id': 'section4-3', 'text': 'Построение модели', 'level': 2, 'order': 21, 'parent': 'section4'},
    {'id': 'section4-4', 'text': 'Оценка модели', 'level': 2, 'order': 22, 'parent': 'section4'},
    {'id': 'section4-5', 'text': 'Пример реализации на Python', 'level': 2, 'order': 23, 'parent': 'section4'},
    {'id': 'section5', 'text': '5. Применение компьютерного зрения', 'level': 1, 'order': 24},
    {'id': 'section5-1', 'text': 'Обработка изображений отходов с помощью CNN', 'level': 2, 'order': 25, 'parent': 'section5'},
    {'id': 'section5-2', 'text': 'Архитектуры нейронных сетей', 'level': 2, 'order': 26, 'parent': 'section5'},
    {'id': 'section5-3', 'text': 'Аугментация данных', 'level': 2, 'order': 27, 'parent': 'section5'},
    {'id': 'section5-4', 'text': 'Пример: автоматическая классификация бытовых отходов', 'level': 2, 'order': 28, 'parent': 'section5'},
]
