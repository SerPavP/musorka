#!/bin/bash

# ============================================
# Автоматический скрипт деплоя Django проекта
# на Google Cloud Platform VM
# Домен: wasteclfmodel.kz
# ============================================

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка, что скрипт запущен от root или с sudo
if [ "$EUID" -ne 0 ]; then 
    log_error "Пожалуйста, запустите скрипт с sudo: sudo bash deploy.sh"
    exit 1
fi

log_info "Начинаем установку и деплой проекта..."

# ============================================
# 1. Обновление системы
# ============================================
log_info "Обновление системы..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y

# ============================================
# 2. Установка системных зависимостей
# ============================================
log_info "Установка системных зависимостей..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    git \
    certbot \
    python3-certbot-nginx \
    supervisor \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# ============================================
# 3. Создание пользователя для приложения (если не существует)
# ============================================
APP_USER="django"
if ! id "$APP_USER" &>/dev/null; then
    log_info "Создание пользователя $APP_USER..."
    useradd -m -s /bin/bash $APP_USER
else
    log_info "Пользователь $APP_USER уже существует"
fi

# ============================================
# 4. Определение пути к проекту
# ============================================
# Определяем домашнюю директорию реального пользователя (не root)
if [ -n "$SUDO_USER" ]; then
    REAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    REAL_HOME="$HOME"
fi

# Проект будет находиться в домашней директории пользователя
PROJECT_DIR="$REAL_HOME/musorka"
log_info "Путь к проекту: $PROJECT_DIR"

# ============================================
# 5. Проверка наличия проекта
# ============================================
log_info "Проверка наличия проекта..."

# Проверяем, существует ли директория проекта
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "Проект не найден в $PROJECT_DIR"
    log_error "Пожалуйста, клонируйте проект:"
    log_error "  git clone https://github.com/SerPavP/musorka.git $PROJECT_DIR"
    exit 1
fi

# Проверяем наличие manage.py (признак Django проекта)
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    log_error "В директории $PROJECT_DIR не найден файл manage.py"
    log_error "Убедитесь, что проект клонирован правильно"
    exit 1
fi

log_info "Проект найден в $PROJECT_DIR"
cd $PROJECT_DIR

# Устанавливаем права доступа на проект
chown -R $APP_USER:$APP_USER $PROJECT_DIR

# ============================================
# 6. Создание виртуального окружения
# ============================================
log_info "Создание виртуального окружения Python..."
if [ ! -d "venv" ]; then
    sudo -u $APP_USER python3 -m venv venv
fi

# ============================================
# 7. Установка Python зависимостей
# ============================================
log_info "Установка Python зависимостей..."
sudo -u $APP_USER $PROJECT_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $PROJECT_DIR/venv/bin/pip install -r requirements.txt
sudo -u $APP_USER $PROJECT_DIR/venv/bin/pip install gunicorn

# ============================================
# 8. Настройка переменных окружения
# ============================================
log_info "Настройка переменных окружения..."
ENV_FILE="$PROJECT_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    log_info "Создание .env файла..."
    # Используем Python из venv для генерации SECRET_KEY
    SECRET_KEY=$(sudo -u $APP_USER bash -c "cd $PROJECT_DIR && source venv/bin/activate && python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'")
    sudo -u $APP_USER cat > $ENV_FILE << EOF
# Django Settings
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=wasteclfmodel.kz,www.wasteclfmodel.kz,localhost,127.0.0.1

# Database (SQLite по умолчанию)
# Для PostgreSQL раскомментируйте и настройте:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=wasteclfmodel
# DB_USER=wasteclfmodel_user
# DB_PASSWORD=your_password_here
# DB_HOST=localhost
# DB_PORT=5432
EOF
    chmod 600 $ENV_FILE
    chown $APP_USER:$APP_USER $ENV_FILE
    log_info ".env файл создан. Пожалуйста, проверьте настройки!"
else
    log_info ".env файл уже существует"
fi

# ============================================
# 9. Обновление settings.py для использования переменных окружения
# ============================================
log_info "Обновление settings.py для production..."
SETTINGS_FILE="$PROJECT_DIR/waste_classification/settings.py"

# Проверяем существование файла
if [ ! -f "$SETTINGS_FILE" ]; then
    log_error "Файл settings.py не найден: $SETTINGS_FILE"
    exit 1
fi

# Создаем backup
cp $SETTINGS_FILE ${SETTINGS_FILE}.backup

# Обновляем SECRET_KEY, DEBUG, ALLOWED_HOSTS
sudo -u $APP_USER python3 << PYTHON_SCRIPT
import re
import os

settings_path = "$SETTINGS_FILE"

with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем импорт os в начало файла (если его нет)
if 'import os' not in content:
    content = content.replace('from pathlib import Path', 'import os\nfrom pathlib import Path')

# Заменяем SECRET_KEY
content = re.sub(
    r"SECRET_KEY = '.*'",
    "SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')",
    content
)

# Заменяем DEBUG
content = re.sub(
    r"DEBUG = True",
    "DEBUG = os.environ.get('DEBUG', 'False') == 'True'",
    content
)

# Заменяем ALLOWED_HOSTS
content = re.sub(
    r"ALLOWED_HOSTS = \[\]",
    "ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []",
    content
)

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Settings.py обновлен успешно")
PYTHON_SCRIPT

# ============================================
# 10. Применение миграций и сбор статики
# ============================================
log_info "Применение миграций базы данных..."
sudo -u $APP_USER bash -c "cd $PROJECT_DIR && source venv/bin/activate && python manage.py migrate --noinput"

log_info "Сбор статических файлов..."
sudo -u $APP_USER bash -c "cd $PROJECT_DIR && source venv/bin/activate && python manage.py collectstatic --noinput"

# Создаем директории для media и staticfiles если их нет
mkdir -p $PROJECT_DIR/media
mkdir -p $PROJECT_DIR/staticfiles
chown -R $APP_USER:$APP_USER $PROJECT_DIR/media
chown -R $APP_USER:$APP_USER $PROJECT_DIR/staticfiles

# ============================================
# 11. Настройка Gunicorn
# ============================================
log_info "Настройка Gunicorn..."
GUNICORN_SOCKET="/run/gunicorn.sock"
mkdir -p /run
chown $APP_USER:$APP_USER /run

# Создаем systemd service для Gunicorn
cat > /etc/systemd/system/wasteclfmodel.service << EOF
[Unit]
Description=wasteclfmodel gunicorn daemon
After=network.target

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
EnvironmentFile=$ENV_FILE
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --access-logfile - \\
    --workers 3 \\
    --bind unix:$GUNICORN_SOCKET \\
    waste_classification.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# ============================================
# 12. Настройка Nginx
# ============================================
log_info "Настройка Nginx..."
DOMAIN="wasteclfmodel.kz"

cat > /etc/nginx/sites-available/wasteclfmodel << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 10M;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$GUNICORN_SOCKET;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Активируем сайт
ln -sf /etc/nginx/sites-available/wasteclfmodel /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации Nginx
nginx -t

# ============================================
# 13. Запуск сервисов
# ============================================
log_info "Запуск сервисов..."

# Перезагружаем systemd
systemctl daemon-reload

# Запускаем Gunicorn
systemctl enable wasteclfmodel
systemctl restart wasteclfmodel

# Перезапускаем Nginx
systemctl restart nginx
systemctl enable nginx

# ============================================
# 14. Настройка SSL сертификата (Let's Encrypt)
# ============================================
log_info "Настройка SSL сертификата..."
log_warn "Убедитесь, что домен $DOMAIN указывает на IP этого сервера!"
log_warn "Проверьте DNS записи перед получением SSL сертификата"

read -p "Получить SSL сертификат сейчас? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
        log_error "Не удалось получить SSL сертификат. Проверьте DNS настройки."
        log_warn "Вы можете получить сертификат позже командой:"
        log_warn "certbot --nginx -d $DOMAIN -d www.$DOMAIN"
    }
else
    log_warn "SSL сертификат не получен. Получите его позже командой:"
    log_warn "certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

# ============================================
# 15. Настройка файрвола (если используется ufw)
# ============================================
log_info "Настройка файрвола..."
if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    log_info "Правила файрвола обновлены"
fi

# ============================================
# 16. Финальная проверка
# ============================================
log_info "Проверка статуса сервисов..."

# Проверка Gunicorn
if systemctl is-active --quiet wasteclfmodel; then
    log_info "✓ Gunicorn работает"
else
    log_error "✗ Gunicorn не запущен. Проверьте: systemctl status wasteclfmodel"
fi

# Проверка Nginx
if systemctl is-active --quiet nginx; then
    log_info "✓ Nginx работает"
else
    log_error "✗ Nginx не запущен. Проверьте: systemctl status nginx"
fi

# ============================================
# 17. Создание суперпользователя (опционально)
# ============================================
log_info "Настройка завершена!"
log_warn "Для создания суперпользователя Django выполните:"
log_warn "sudo -u $APP_USER bash -c 'cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser'"

# ============================================
# Полезные команды
# ============================================
log_info "Полезные команды для управления:"
echo ""
echo "  Проверка статуса Gunicorn:"
echo "    systemctl status wasteclfmodel"
echo ""
echo "  Перезапуск Gunicorn:"
echo "    systemctl restart wasteclfmodel"
echo ""
echo "  Просмотр логов Gunicorn:"
echo "    journalctl -u wasteclfmodel -f"
echo ""
echo "  Перезапуск Nginx:"
echo "    systemctl restart nginx"
echo ""
echo "  Просмотр логов Nginx:"
echo "    tail -f /var/log/nginx/error.log"
echo ""
echo "  Создание суперпользователя:"
echo "    sudo -u $APP_USER bash -c 'cd $PROJECT_DIR && source venv/bin/activate && python manage.py createsuperuser'"
echo ""

log_info "Деплой завершен! Проект должен быть доступен по адресу: http://$DOMAIN"
log_warn "Если вы настроили SSL, используйте: https://$DOMAIN"

