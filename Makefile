# Makefile для проекта Alekhin

# Цвета для вывода
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m

# Основные команды
.PHONY: help setup start stop restart logs clean build migrate test

help: ## Показать справку
	@echo "$(BLUE)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Настроить окружение (генерировать пароли, создать .env)
	@echo "$(BLUE)🚀 Настройка окружения...$(NC)"
	@chmod +x setup.sh
	@./setup.sh

start: ## Запустить все сервисы
	@echo "$(BLUE)🚀 Запуск всех сервисов...$(NC)"
	@echo "$(YELLOW)⏳ Обновление репозитория...$(NC)"
	@git pull origin main
	@echo "$(YELLOW)⏳ Остановка текущих сервисов...$(NC)"
	@docker-compose down
	@docker-compose up --build -d
	@echo "$(GREEN)✅ Сервисы запущены$(NC)"
	@make status

start-dev: ## Запустить сервисы в режиме разработки (с PgAdmin)
	@echo "$(BLUE)🚀 Запуск сервисов в режиме разработки...$(NC)"
	@docker-compose --profile dev up -d
	@echo "$(GREEN)✅ Сервисы запущены с PgAdmin$(NC)"
	@make status

stop: ## Остановить все сервисы
	@echo "$(YELLOW)⏹️  Остановка сервисов...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Сервисы остановлены$(NC)"

restart: ## Перезапустить все сервисы
	@echo "$(YELLOW)🔄 Перезапуск сервисов...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)✅ Сервисы перезапущены$(NC)"

logs: ## Показать логи всех сервисов
	@docker-compose logs -f

logs-backend: ## Показать логи backend
	@docker-compose logs -f backend

logs-db: ## Показать логи базы данных
	@docker-compose logs -f db

status: ## Показать статус сервисов
	@echo "$(BLUE)📊 Статус сервисов:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)🌐 Доступные URL:$(NC)"
	@echo "  Backend:    http://localhost:8000"
	@echo "  Frontend:   http://localhost:3002"
	@echo "  Admin:      http://localhost:3001"
	@echo "  PgAdmin:    http://localhost:5050 (только в dev режиме)"

build: ## Пересобрать все образы
	@echo "$(BLUE)🔨 Пересборка образов...$(NC)"
	@docker-compose build --no-cache
	@echo "$(GREEN)✅ Образы пересобраны$(NC)"

migrate: ## Выполнить миграции Django
	@echo "$(BLUE)🗄️  Выполнение миграций...$(NC)"
	@docker-compose exec backend python manage.py migrate
	@echo "$(GREEN)✅ Миграции выполнены$(NC)"

makemigrations: ## Создать новые миграции Django
	@echo "$(BLUE)📝 Создание миграций...$(NC)"
	@docker-compose exec backend python manage.py makemigrations
	@echo "$(GREEN)✅ Миграции созданы$(NC)"

createsuperuser: ## Создать суперпользователя Django
	@echo "$(BLUE)👤 Создание суперпользователя...$(NC)"
	@docker-compose exec backend python manage.py createsuperuser

shell: ## Открыть shell Django
	@docker-compose exec backend python manage.py shell

dbshell: ## Открыть shell PostgreSQL
	@docker-compose exec db psql -U postgres -d postgres

backup-db: ## Создать бэкап базы данных
	@echo "$(BLUE)💾 Создание бэкапа базы данных...$(NC)"
	@mkdir -p data/backups
	@docker-compose exec db pg_dump -U postgres -d postgres > data/backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)✅ Бэкап создан в data/backups/$(NC)"

restore-db: ## Восстановить базу данных из бэкапа (использование: make restore-db BACKUP=filename.sql)
	@echo "$(BLUE)🔄 Восстановление базы данных...$(NC)"
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)❌ Укажите файл бэкапа: make restore-db BACKUP=filename.sql$(NC)"; \
		exit 1; \
	fi
	@docker-compose exec -T db psql -U postgres -d postgres < data/backups/$(BACKUP)
	@echo "$(GREEN)✅ База данных восстановлена$(NC)"

clean: ## Очистить все (контейнеры, образы, volumes)
	@echo "$(RED)🧹 Очистка всех ресурсов...$(NC)"
	@read -p "Вы уверены? Это удалит ВСЕ данные! (y/N): " confirm && [ "$confirm" = "y" ]
	@docker-compose down -v --remove-orphans
	@docker system prune -af --volumes
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

clean-soft: ## Мягкая очистка (только контейнеры)
	@echo "$(YELLOW)🧹 Мягкая очистка...$(NC)"
	@docker-compose down --remove-orphans
	@docker container prune -f
	@echo "$(GREEN)✅ Контейнеры очищены$(NC)"

test: ## Запустить тесты Django
	@echo "$(BLUE)🧪 Запуск тестов...$(NC)"
	@docker-compose exec backend python manage.py test
	@echo "$(GREEN)✅ Тесты завершены$(NC)"

install-deps: ## Установить зависимости Python
	@echo "$(BLUE)📦 Установка зависимостей...$(NC)"
	@docker-compose exec backend pip install -r requirements.txt
	@echo "$(GREEN)✅ Зависимости установлены$(NC)"

collectstatic: ## Собрать статические файлы
	@echo "$(BLUE)📂 Сбор статических файлов...$(NC)"
	@docker-compose exec backend python manage.py collectstatic --noinput
	@echo "$(GREEN)✅ Статические файлы собраны$(NC)"

check: ## Проверить настройки Django
	@echo "$(BLUE)✅ Проверка настроек Django...$(NC)"
	@docker-compose exec backend python manage.py check

generate-password: ## Сгенерировать новый случайный пароль
	@echo "$(BLUE)🔐 Генерация нового пароля:$(NC)"
	@python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(16)))"

# Команды для разработки
dev-setup: setup start-dev migrate createsuperuser ## Полная настройка для разработки

quick-restart: ## Быстрый перезапуск backend
	@echo "$(YELLOW)⚡ Быстрый перезапуск backend...$(NC)"
	@docker-compose restart backend
	@echo "$(GREEN)✅ Backend перезапущен$(NC)"

watch-logs: ## Отслеживать логи в реальном времени
	@docker-compose logs -f --tail=100

# Команды для production
prod-start: ## Запустить в production режиме
	@echo "$(BLUE)🚀 Запуск в production режиме...$(NC)"
	@docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production сервисы запущены$(NC)"

prod-stop: ## Остановить production сервисы
	@docker-compose -f docker-compose.prod.yml down

# Информационные команды
env-info: ## Показать информацию о переменных окружения
	@echo "$(BLUE)🔧 Информация о переменных окружения:$(NC)"
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ Файл .env найден$(NC)"; \
		echo "Основные переменные:"; \
		grep -E "^(POSTGRES_|DJANGO_|REDIS_|JWT_)" .env | sed 's/=.*/=***/' || true; \
	else \
		echo "$(RED)❌ Файл .env не найден$(NC)"; \
		echo "Запустите: make setup"; \
	fi

docker-info: ## Показать информацию о Docker
	@echo "$(BLUE)🐳 Информация о Docker:$(NC)"
	@docker --version
	@docker-compose --version
	@echo ""
	@echo "$(BLUE)📊 Использование ресурсов:$(NC)"
	@docker system df

# Команды для мониторинга
monitor: ## Показать использование ресурсов контейнерами
	@echo "$(BLUE)📊 Мониторинг ресурсов:$(NC)"
	@docker stats --no-stream

ports: ## Показать занятые порты
	@echo "$(BLUE)🔌 Занятые порты:$(NC)"
	@netstat -tlnp 2>/dev/null | grep -E ":(8000|3001|3002|5432|5050|6379)" || echo "Порты свободны"

# Команды для обслуживания
update: ## Обновить все образы
	@echo "$(BLUE)🔄 Обновление образов...$(NC)"
	@docker-compose pull
	@docker-compose build --pull
	@echo "$(GREEN)✅ Образы обновлены$(NC)"

volumes-info: ## Показать информацию о volumes
	@echo "$(BLUE)💾 Информация о volumes:$(NC)"
	@docker volume ls | grep -E "(postgres_data|redis_data|pgadmin_data)"
	@echo ""
	@docker system df -v | grep -A 20 "Local Volumes"