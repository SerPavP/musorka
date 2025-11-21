import os
import numpy as np
from PIL import Image
import tensorflow as tf
import tf_keras as keras  # Используем tf_keras для совместимости со старыми моделями
from django.conf import settings

# Категории отходов (из ноутбука EfficientNet)
CATEGORIES = ['battery', 'biological', 'cardboard', 'clothes', 'glass',
              'metal', 'paper', 'plastic', 'shoes', 'trash']

# Русские названия категорий для отображения
CATEGORIES_RU = {
    'battery': 'Батарейки',
    'biological': 'Органические отходы',
    'cardboard': 'Картон',
    'clothes': 'Одежда',
    'glass': 'Стекло',
    'metal': 'Металл',
    'paper': 'Бумага',
    'plastic': 'Пластик',
    'shoes': 'Обувь',
    'trash': 'Прочий мусор'
}

# Соответствие категорий мусорным контейнерам
WASTE_BINS = {
    'battery': 'специальный контейнер для батареек',
    'biological': 'контейнер для органических отходов',
    'cardboard': 'контейнер для бумаги и картона',
    'clothes': 'контейнер для текстиля',
    'glass': 'контейнер для стекла',
    'metal': 'контейнер для металла',
    'paper': 'контейнер для бумаги',
    'plastic': 'контейнер для пластика',
    'shoes': 'контейнер для текстиля',
    'trash': 'контейнер для прочего мусора'
}

# Глобальная переменная для модели
_model = None

def get_model():
    """Загружает модель EfficientNet классификации отходов"""
    global _model
    if _model is None:
        # Загружаем модель EfficientNet из ob_model
        model_path = os.path.join(settings.BASE_DIR, 'ob_model', 'waste_classifier_efficientnet.h5')
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Модель не найдена по пути: {model_path}")
        
        # Используем tf_keras для загрузки легаси модели
        try:
            # tf_keras предназначен для загрузки моделей Keras 2.x в TensorFlow 2.16+
            os.environ["TF_USE_LEGACY_KERAS"] = "1"
            _model = keras.models.load_model(model_path, compile=False)
        except Exception as e:
            raise RuntimeError(
                f"Не удалось загрузить модель с помощью tf_keras: {e}\n"
                f"Убедитесь, что установлены пакеты: tensorflow>=2.16 и tf_keras"
            )
    
    return _model

def preprocess_image(image_path):
    """Предобрабатывает изображение для классификации (224x224, как в ноутбуке)"""
    IMG_SIZE = 224
    
    # Загружаем изображение через PIL (как в ноутбуке)
    img = Image.open(image_path).convert('RGB')
    img_resized = img.resize((IMG_SIZE, IMG_SIZE))
    
    # Преобразуем в numpy массив и нормализуем
    x = np.array(img_resized) / 255.0
    
    # Добавляем размерность батча
    x = np.expand_dims(x, axis=0)
    
    return x

def classify_waste(image_path):
    """Классифицирует изображение отходов"""
    model = get_model()
    
    # Предобрабатываем изображение
    img_array = preprocess_image(image_path)
    
    # Делаем предсказание
    predictions = model.predict(img_array, verbose=0)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx]) * 100  # В процентах
    
    # Получаем название класса
    predicted_class = CATEGORIES[predicted_class_idx]
    predicted_class_ru = CATEGORIES_RU[predicted_class]
    
    # Получаем информацию о мусорном контейнере
    waste_bin = WASTE_BINS[predicted_class]
    
    # Создаем словарь всех предсказаний с русскими названиями
    all_predictions = {}
    for i in range(len(CATEGORIES)):
        class_name = CATEGORIES[i]
        class_name_ru = CATEGORIES_RU[class_name]
        all_predictions[class_name_ru] = float(predictions[0][i]) * 100
    
    # Сортируем предсказания по убыванию вероятности
    all_predictions_sorted = dict(sorted(all_predictions.items(), key=lambda x: x[1], reverse=True))
    
    return {
        'class': predicted_class,
        'class_ru': predicted_class_ru,
        'waste_bin': waste_bin,
        'confidence': confidence,
        'all_predictions': all_predictions_sorted
    }
