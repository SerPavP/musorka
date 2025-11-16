import os
import numpy as np
import cv2
import tensorflow as tf
from django.conf import settings

# Категории отходов
CATEGORIES = ['Glass', 'Metal', 'Organic', 'Paper', 'Plastic', 'Trash']

# Соответствие категорий мусорным контейнерам
WASTE_BINS = {
    'Glass': 'контейнер для стекла',
    'Metal': 'контейнер для металла',
    'Organic': 'контейнер для органических отходов',
    'Paper': 'контейнер для бумаги',
    'Plastic': 'контейнер для пластика',
    'Trash': 'контейнер для прочего мусора'
}

# Глобальная переменная для модели
_model = None

def load_model():
    """Загружает модель классификации отходов"""
    global _model
    if _model is None:
        # Создаем модель такую же, как в ноутбуке
        _model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', input_shape=(64, 64, 3)),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(units=512, activation='relu'),
            tf.keras.layers.Dense(units=6, activation='softmax')
        ])
        
        # Компилируем модель
        _model.compile(
            loss='categorical_crossentropy',
            optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.001),
            metrics=['accuracy']
        )
        
        # Пытаемся загрузить веса, если они есть
        weights_path = os.path.join(settings.BASE_DIR, 'classifier', 'model_weights.h5')
        if os.path.exists(weights_path):
            _model.load_weights(weights_path)
    
    return _model

def preprocess_image(image_path):
    """Предобрабатывает изображение для классификации"""
    IMG_SIZE = 64
    
    # Читаем изображение
    img_array = cv2.imread(image_path)
    if img_array is None:
        raise ValueError("Не удалось загрузить изображение")
    
    # Изменяем размер
    new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
    
    # Нормализуем
    new_array = new_array.astype('float32')
    new_array = new_array / 255.0
    
    # Добавляем размерность батча
    new_array = np.expand_dims(new_array, axis=0)
    
    return new_array

def classify_waste(image_path):
    """Классифицирует изображение отходов"""
    model = load_model()
    
    # Предобрабатываем изображение
    img_array = preprocess_image(image_path)
    
    # Делаем предсказание
    predictions = model.predict(img_array, verbose=0)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx]) * 100  # В процентах
    
    # Получаем название класса
    predicted_class = CATEGORIES[predicted_class_idx]
    
    # Получаем информацию о мусорном контейнере
    waste_bin = WASTE_BINS[predicted_class]
    
    return {
        'class': predicted_class,
        'waste_bin': waste_bin,
        'confidence': confidence,
        'all_predictions': {CATEGORIES[i]: float(predictions[0][i]) * 100 for i in range(len(CATEGORIES))}
    }

