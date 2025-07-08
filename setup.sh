#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Настройка окружения для проекта Alekhin${NC}"
echo "================================================"

# Функция для генерации случайного пароля
generate_password() {
    local length=${1:-16}
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#\$%^&*'
password = ''.join(secrets.choice(alphabet) for _ in range($length))
print(password)
"
}

# Проверяем наличие .env файла
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Файл .env уже существует${NC}"
    read -p "Хотите перезаписать его? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}ℹ️  Использую существующий .env файл${NC}"
        exit 0
    fi
fi

echo -e "${GREEN}🔐 Генерация паролей...${NC}"

# Генерируем пароли
POSTGRES_PASSWORD=$(generate_password 16)
DJANGO_SECRET_KEY=$(generate_password 50)
PGADMIN_PASSWORD=$(generate_password 12)

echo -e "${GREEN}✅ Пароли сгенерированы${NC}"

# Создаем .env файл
cat > .env << EOF
# ==============================================
# DATABASE CONFIGURATION
# ==============================================
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_HOST=db
POSTGRES_PORT=5432

# ==============================================
# DJANGO CONFIGURATION
# ==============================================
DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# ==============================================
# JWT CONFIGURATION
# ==============================================
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# ==============================================
# CORS CONFIGURATION
# ==============================================
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True

# ==============================================
# CACHE CONFIGURATION (REDIS)
# ==============================================
REDIS_URL=redis://redis:6379/1
ITEMS_COUNT_CACHE_TIMEOUT=300

# ==============================================
# PGADMIN CONFIGURATION (для разработки)
# ==============================================
PGADMIN_DEFAULT_EMAIL=admin@alekhin.local
PGADMIN_DEFAULT_PASSWORD=${PGADMIN_PASSWORD}
PGADMIN_LISTEN_PORT=5050

# ==============================================
# APPLICATION PORTS
# ==============================================
BACKEND_PORT=8000
FRONTEND_PORT=3002
ADMIN_PORT=3001
POSTGRES_EXTERNAL_PORT=5432
PGADMIN_EXTERNAL_PORT=5050

# ==============================================
# VOLUMES PATHS
# ==============================================
DATA_PATH=./data
MEDIA_PATH=./media
CONFIG_PATH=./config
EOF

echo -e "${GREEN}✅ Файл .env создан${NC}"

# Создаем необходимые директории
echo -e "${BLUE}📁 Создание директорий...${NC}"
mkdir -p data/backups
mkdir -p media
mkdir -p config/pgadmin

echo -e "${GREEN}✅ Директории созданы${NC}"

# Создаем конфигурацию для PgAdmin
cat > config/pgadmin/servers.json << EOF
{
  "Servers": {
    "1": {
      "Name": "Alekhin PostgreSQL",
      "Group": "Servers",
      "Host": "db",
      "Port": 5432,
      "MaintenanceDB": "postgres",
      "Username": "postgres",
      "SSLMode": "prefer",
      "Timeout": 10,
      "UseSSHTunnel": 0
    }
  }
}
EOF

echo -e "${GREEN}✅ Конфигурация PgAdmin создана${NC}"

# Выводим информацию о созданных паролях
echo ""
echo -e "${YELLOW}🔑 Сгенерированные пароли:${NC}"
echo "================================================"
echo -e "PostgreSQL пароль: ${GREEN}${POSTGRES_PASSWORD}${NC}"
echo -e "PgAdmin пароль: ${GREEN}${PGADMIN_PASSWORD}${NC}"
echo -e "Django SECRET_KEY: ${GREEN}${DJANGO_SECRET_KEY:0:20}...${NC}"
echo ""
echo -e "${BLUE}📝 Важно:${NC}"
echo "- Сохраните эти пароли в безопасном месте"
echo "- Не добавляйте .env файл в git репозиторий"
echo "- Файл .env уже добавлен в .gitignore"
echo ""

# Проверяем наличие .gitignore и добавляем .env если его нет
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.env$" .gitignore; then
        echo ".env" >> .gitignore
        echo -e "${GREEN}✅ .env добавлен в .gitignore${NC}"
    fi
else
    echo ".env" > .gitignore
    echo -e "${GREEN}✅ Создан .gitignore с .env${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Настройка завершена!${NC}"
echo ""
echo -e "${BLUE}Следующие шаги:${NC}"
echo "1. Проверьте настройки в .env файле"
echo "2. Запустите проект: docker-compose up -d"
echo "3. Для разработки с PgAdmin: docker-compose --profile dev up -d"
echo ""
echo -e "${BLUE}Доступ к сервисам:${NC}"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3002"
echo "- Admin Panel: http://localhost:3001"
echo "- PgAdmin (dev): http://localhost:5050"
echo "  Email: admin@alekhin.local"
echo "  Пароль: ${PGADMIN_PASSWORD}"