# Django-проект: Классификация отходов (ML + веб)

Хочу, чтобы ты помог мне полностью собрать Django-проект с интеграцией готовой модели машинного обучения (классификация отходов по картинке). Я буду запускать этот проект локально и дорабатывать его в Cursor.

---

## 1. Общая задача

Нужно создать Django-сайт, который:

1. Имеет **главную страницу** с краткой информацией о проекте и учебном пособии.
2. Имеет в шапке кнопку **«Пример машинного обучения»**.
3. При нажатии на кнопку открывается отдельная страница:
   - форма загрузки изображения (фото отходов);
   - используется сохранённая модель Keras (из `waste_clf_model.h5`);
   - модель классифицирует изображение и:
     - показывает класс отходов (`glass`, `metal`, `organic`, `paper`, `plastic`, `trash`);
     - пишет, в какой контейнер (мусорку) нужно выбрасывать этот объект;
     - опционально показывает таблицу вероятностей по всем классам.

Главная страница по стилю может быть простой, но аккуратной (Bootstrap 5, светлая тема), не обязательно копировать сайт 1 в 1, главное — структура и читаемость.

---

## 2. Данные, которые у меня уже есть

1. **Jupyter-ноутбук** `waste_clf_model.ipynb` с обученной CNN-моделью Keras.
2. В ноутбуке список классов примерно такой:

   ```python
   ctg = ['glass', 'metal', 'organic', 'paper', 'plastic', 'trash']
Текст учебного пособия в Word-файле (я сам вставлю подробный текст позже). На главной странице сейчас достаточно краткой информации (см. ниже).

3. Как использовать модель (Keras)
Сделай так, чтобы Django-проект использовал сохранённую модель в формате .h5.

Добавь в проект (в комментариях) пример кода, который я вставлю в конец ноутбука и выполню там:

python
Копировать код
# В ноутбуке waste_clf_model.ipynb
from tensorflow.keras.models import save_model

# Предположим, что обученная модель называется cnn_model
cnn_model.save('waste_clf_model.h5')
В Django-проекте предположим, что файл waste_clf_model.h5 лежит в корне проекта (рядом с manage.py).

В Django-коде сделай:

python
Копировать код
CLASS_NAMES = ['glass', 'metal', 'organic', 'paper', 'plastic', 'trash']

CONTAINER_TEXT = {
    'glass':   'Контейнер для стекла',
    'metal':   'Контейнер для металла',
    'organic': 'Контейнер для органических отходов (пищевые)',
    'paper':   'Контейнер для бумаги и картона',
    'plastic': 'Контейнер для пластика',
    'trash':   'Общий контейнер для несортируемых отходов',
}
Предобработка изображения:

открыть через PIL.Image.open;

перевести в RGB;

изменить размер на (64, 64) (если в ноутбуке другой размер — комментарий, где это можно поменять);

нормализовать в [0, 1];

добавить размер батча np.expand_dims(img_arr, axis=0) → форма (1, 64, 64, 3).

Использование:

python
Копировать код
preds = MODEL.predict(arr)
class_idx = int(np.argmax(preds, axis=1)[0])
label = CLASS_NAMES[class_idx]
recommendation = CONTAINER_TEXT.get(label, 'Неизвестный тип отхода')
4. Структура проекта (Django)
Создай стандартный Django-проект со структурой:

text
Копировать код
waste_site/              # корень проекта
  manage.py
  waste_site/
    __init__.py
    settings.py
    urls.py
    wsgi.py
  core/
    __init__.py
    urls.py
    views.py
    forms.py
    templates/
      base.html
      index.html
      ml_example.html
  static/
    css/
      main.css
waste_clf_model.h5       # сюда я сам положу модель
4.1. Настройки (settings.py)
В waste_site/settings.py:

Добавь 'core' в INSTALLED_APPS.

Добавь конфиг для статики и медиа:

python
Копировать код
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    # ...
    'core',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
Остальное можно оставить по умолчанию (Django 4+).

4.2. Корневой urls.py
waste_site/urls.py:

python
Копировать код
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
4.3. urls.py приложения core
Создай core/urls.py:

python
Копировать код
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ml-example/', views.ml_example, name='ml_example'),
]
5. Форма и views для классификации
5.1. Форма загрузки изображения
core/forms.py:

python
Копировать код
from django import forms

class WasteImageForm(forms.Form):
    image = forms.ImageField(label='Выберите изображение отхода')
5.2. Views
core/views.py:

Импортируй нужные модули.

Реализуй два обработчика: index и ml_example.

Загрузку модели сделай один раз при загрузке модуля.

Пример логики (можешь дооформить, но суть такая):

python
Копировать код
import os
import numpy as np
from PIL import Image

from django.conf import settings
from django.shortcuts import render

from tensorflow.keras.models import load_model

from .forms import WasteImageForm

MODEL_PATH = os.path.join(settings.BASE_DIR, 'waste_clf_model.h5')
MODEL = load_model(MODEL_PATH)

CLASS_NAMES = ['glass', 'metal', 'organic', 'paper', 'plastic', 'trash']

CONTAINER_TEXT = {
    'glass':   'Контейнер для стекла',
    'metal':   'Контейнер для металла',
    'organic': 'Контейнер для органических отходов (пищевые)',
    'paper':   'Контейнер для бумаги и картона',
    'plastic': 'Контейнер для пластика',
    'trash':   'Общий контейнер для несортируемых отходов',
}


def index(request):
    """
    Главная страница с краткой информацией о проекте и учебном пособии.
    Подробный текст я вставлю позже.
    """
    return render(request, 'index.html')


def ml_example(request):
    """
    Страница с примером машинного обучения.
    Пользователь загружает изображение отхода,
    а модель определяет класс и рекомендует контейнер.
    """
    context = {}

    if request.method == 'POST':
        form = WasteImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']

            # 1. Открываем изображение и приводим к нужному виду
            img = Image.open(image_file).convert('RGB')
            img = img.resize((64, 64))  # если другое размерность - можно изменить здесь

            arr = np.array(img, dtype='float32') / 255.0
            arr = np.expand_dims(arr, axis=0)  # (1, 64, 64, 3)

            # 2. Предсказание модели
            preds = MODEL.predict(arr)
            class_idx = int(np.argmax(preds, axis=1)[0])
            label = CLASS_NAMES[class_idx]
            recommendation = CONTAINER_TEXT.get(label, 'Неизвестный тип отхода')

            probabilities = list(zip(CLASS_NAMES, preds[0].tolist()))

            context.update({
                'form': form,
                'prediction': label,
                'recommendation': recommendation,
                'probabilities': probabilities,
            })
        else:
            context['form'] = form
    else:
        form = WasteImageForm()
        context['form'] = form

    return render(request, 'ml_example.html', context)
6. Шаблоны (templates)
Используй Bootstrap 5 через CDN. Все шаблоны положи в core/templates/.

6.1. base.html
Базовый шаблон, в шапке кнопка «Пример машинного обучения».

html
Копировать код
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Классификация отходов — машинное обучение</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap 5 -->
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
    >

    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom">
  <div class="container">
    <a class="navbar-brand fw-semibold" href="{% url 'index' %}">
      Машинное и глубокое обучение
    </a>

    <div class="ms-auto">
      <a href="{% url 'ml_example' %}" class="btn btn-primary">
        Пример машинного обучения
      </a>
    </div>
  </div>
</nav>

<main class="container my-4">
  {% block content %}{% endblock %}
</main>

<footer class="border-top py-3 mt-5 text-muted small">
  <div class="container">
    © 2025. Учебный проект по классификации отходов.
  </div>
</footer>

</body>
</html>
6.2. index.html (главная страница)
На главной ОБЯЗАТЕЛЬНО должен быть следующий текст:

Название: Классификация отходов с использованием методов интеллектуального анализа данных

Электронное учебное пособие для студентов инженерных специальностей.

Авторы: Айдынқызы Айдана , Рахимжанова Ляззат Болтабаевна

Учебное заведение: КазНУ имени аль_Фараби

Год: 2021

Сделай аккуратный блок с этой информацией и несколько секций-плейсхолдеров под будущий текст.

html
Копировать код
{% extends "base.html" %}

{% block content %}
  <section class="py-4">
    <h1 class="h2 mb-3">
      Классификация отходов с использованием методов интеллектуального анализа данных
    </h1>

    <div class="card mb-4">
      <div class="card-body">
        <p class="mb-1"><strong>Название:</strong> Классификация отходов с использованием методов интеллектуального анализа данных</p>
        <p class="mb-1">Электронное учебное пособие для студентов инженерных специальностей.</p>
        <p class="mb-1"><strong>Авторы:</strong> Айдынқызы Айдана , Рахимжанова Ляззат Болтабаевна</p>
        <p class="mb-1"><strong>Учебное заведение:</strong> КазНУ имени аль_Фараби</p>
        <p class="mb-0"><strong>Год:</strong> 2021</p>
      </div>
    </div>

    <p class="text-muted">
      Ниже будут размещены разделы электронного учебного пособия. Подробный текст я вставлю позже.
    </p>
  </section>

  <section class="mb-4">
    <h2 class="h4">Введение</h2>
    <p>
      <!-- Плейсхолдер: сюда я вставлю текст из раздела "Введение" из Word-документа -->
    </p>
  </section>

  <section class="mb-4">
    <h2 class="h4">Цель и задачи пособия</h2>
    <p>
      <!-- Плейсхолдер: цель, задачи, актуальность применения методов интеллектуального анализа данных к проблеме отходов -->
    </p>
  </section>

  <section class="mb-4">
    <h2 class="h4">Методы и технологии интеллектуального анализа данных</h2>
    <p>
      <!-- Плейсхолдер: краткое описание используемых методов машинного обучения, признаков и архитектуры модели -->
    </p>
  </section>

  <section class="mb-4">
    <h2 class="h4">Практический пример: классификация отходов по изображению</h2>
    <p>
      В рамках пособия реализован веб-сервис, демонстрирующий работу модели классификации отходов по фотографии.
      Пользователь может загрузить изображение, после чего система предложит соответствующий тип контейнера
      для выброса. Чтобы попробовать, нажмите кнопку «Пример машинного обучения» в верхней части страницы.
    </p>
  </section>
{% endblock %}
6.3. ml_example.html (страница примера ML)
html
Копировать код
{% extends "base.html" %}

{% block content %}
  <h1 class="h3 mb-3">Пример машинного обучения: классификация отходов по изображению</h1>
  <p class="text-muted">
    Загрузите фотографию отхода, и модель подскажет, в какой контейнер его выбрасывать.
  </p>

  <form method="post" enctype="multipart/form-data" class="card p-3 mb-4">
    {% csrf_token %}
    <div class="mb-3">
      {{ form.image.label_tag }}
      {{ form.image }}
      {% if form.image.errors %}
        <div class="text-danger small">{{ form.image.errors }}</div>
      {% endif %}
    </div>
    <button type="submit" class="btn btn-success">Классифицировать</button>
  </form>

  {% if prediction %}
    <div class="alert alert-info">
      <p class="mb-1">
        <strong>Класс модели:</strong> {{ prediction }}
      </p>
      <p class="mb-0">
        <strong>Рекомендация:</strong> {{ recommendation }}
      </p>
    </div>

    {% if probabilities %}
      <h2 class="h5 mt-4">Вероятности по классам</h2>
      <table class="table table-sm">
        <thead>
          <tr>
            <th>Класс</th>
            <th>Вероятность</th>
          </tr>
        </thead>
        <tbody>
          {% for name, prob in probabilities %}
            <tr>
              <td>{{ name }}</td>
              <td>{{ prob|floatformat:3 }}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% endif %}
  {% endif %}
{% endblock %}
7. Статика и стили
Создай файл static/css/main.css (можно оставить минимальным, просто чтобы был):

css
Копировать код
body {
    /* при необходимости можно оформить фон/отступы */
}

.card p {
    margin-bottom: 0.35rem;
}
8. Зависимости (requirements.txt)
Создай файл requirements.txt с примерным набором:

text
Копировать код
Django>=4.2
Pillow
tensorflow
numpy
9. Что нужно сделать целиком
Создать весь Django-проект со структурой и файлами, описанными выше.

Вставить пример кода / комментарии для сохранения модели в .h5 из ноутбука.

Обеспечить корректную загрузку модели waste_clf_model.h5 и обработку изображения.

Сделать главную страницу с указанным обязательным текстом и плейсхолдерами под остальной материал.

Сделать страницу примера ML с формой загрузки изображения и отображением результата.

Сгенерируй, пожалуйста, весь этот проект (все файлы) на основе этого описания.