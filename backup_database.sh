#!/bin/bash
# backup_database.sh
# Автоматический бэкап базы данных PostgreSQL для Alekhin Clinic

set -e  # Остановка при ошибке

# ===========================================
# КОНФИГУРАЦИЯ
# ===========================================

# Настройки базы данных (из docker-compose.yaml)
DB_NAME="postgres"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"
DB_CONTAINER="backend"  # Имя контейнера с Django

# Настройки бэкапа
BACKUP_DIR="/backups"
RETENTION_DAYS=30  # Сколько дней хранить бэкапы
MAX_BACKUPS=100    # Максимальное количество бэкапов

# Настройки уведомлений (опционально)
TELEGRAM_BOT_TOKEN=""  # Токен Telegram бота для уведомлений
TELEGRAM_CHAT_ID=""    # ID чата для уведомлений
EMAIL_RECIPIENT=""     # Email для уведомлений

# ===========================================
# ФУНКЦИИ
# ===========================================

# Цветной вывод
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Создание директории для бэкапов
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log_info "Создание директории бэкапов: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
    fi
}

# Проверка доступности базы данных
check_database() {
    log_info "Проверка доступности базы данных..."
    
    if docker ps | grep -q "$DB_CONTAINER"; then
        log_success "Контейнер $DB_CONTAINER запущен"
    else
        log_error "Контейнер $DB_CONTAINER не запущен!"
        exit 1
    fi
    
    # Проверка подключения к БД
    if docker exec "$DB_CONTAINER" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
        log_success "База данных доступна"
    else
        log_error "База данных недоступна!"
        exit 1
    fi
}

# Создание бэкапа
create_backup() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_filename="alekhin_clinic_backup_${timestamp}.sql"
    local backup_path="$BACKUP_DIR/$backup_filename"
    
    log_info "Создание бэкапа базы данных..."
    log_info "Файл: $backup_filename"
    
    # Создание бэкапа через Docker
    if docker exec "$DB_CONTAINER" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain > "$backup_path" 2>/dev/null; then
        
        log_success "Бэкап создан успешно: $backup_filename"
        
        # Сжатие бэкапа
        log_info "Сжатие бэкапа..."
        gzip "$backup_path"
        backup_path="${backup_path}.gz"
        
        # Проверка размера файла
        local file_size=$(du -h "$backup_path" | cut -f1)
        log_success "Бэкап сжат. Размер: $file_size"
        
        echo "$backup_path"  # Возвращаем путь к файлу
    else
        log_error "Ошибка создания бэкапа!"
        exit 1
    fi
}

# Создание бэкапа медиафайлов
backup_media() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local media_backup="$BACKUP_DIR/media_backup_${timestamp}.tar.gz"
    local media_dir="./media"  # Путь к медиафайлам
    
    if [ -d "$media_dir" ]; then
        log_info "Создание бэкапа медиафайлов..."
        
        if tar -czf "$media_backup" -C "$(dirname "$media_dir")" "$(basename "$media_dir")" 2>/dev/null; then
            local file_size=$(du -h "$media_backup" | cut -f1)
            log_success "Бэкап медиафайлов создан. Размер: $file_size"
            echo "$media_backup"
        else
            log_warning "Ошибка создания бэкапа медиафайлов"
        fi
    else
        log_warning "Директория медиафайлов не найдена: $media_dir"
    fi
}

# Очистка старых бэкапов
cleanup_old_backups() {
    log_info "Очистка бэкапов старше $RETENTION_DAYS дней..."
    
    local deleted_count=0
    
    # Удаление по времени
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -type f | while read -r file; do
        log_info "Удаление старого бэкапа: $(basename "$file")"
        rm -f "$file"
        ((deleted_count++))
    done
    
    find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +$RETENTION_DAYS -type f | while read -r file; do
        log_info "Удаление старого бэкапа медиа: $(basename "$file")"
        rm -f "$file"
        ((deleted_count++))
    done
    
    # Удаление лишних файлов (оставляем только MAX_BACKUPS самых новых)
    local db_backups_count=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f | wc -l)
    if [ "$db_backups_count" -gt "$MAX_BACKUPS" ]; then
        local excess=$((db_backups_count - MAX_BACKUPS))
        log_info "Удаление $excess лишних бэкапов БД..."
        
        find "$BACKUP_DIR" -name "*.sql.gz" -type f -printf '%T@ %p\n' | \
        sort -n | head -n "$excess" | cut -d' ' -f2- | \
        while read -r file; do
            log_info "Удаление: $(basename "$file")"
            rm -f "$file"
        done
    fi
    
    log_success "Очистка завершена"
}

# Отправка уведомления в Telegram
send_telegram_notification() {
    local message="$1"
    
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST \
            "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$message" \
            -d "parse_mode=Markdown" > /dev/null 2>&1
    fi
}

# Отправка email уведомления
send_email_notification() {
    local subject="$1"
    local message="$2"
    
    if [ -n "$EMAIL_RECIPIENT" ]; then
        echo "$message" | mail -s "$subject" "$EMAIL_RECIPIENT" 2>/dev/null || true
    fi
}

# Проверка целостности бэкапа
verify_backup() {
    local backup_file="$1"
    
    log_info "Проверка целостности бэкапа..."
    
    if [ -f "$backup_file" ]; then
        # Проверка, что файл не пустой
        if [ -s "$backup_file" ]; then
            # Проверка, что это валидный gzip файл
            if gzip -t "$backup_file" 2>/dev/null; then
                log_success "Бэкап прошел проверку целостности"
                return 0
            else
                log_error "Бэкап поврежден (невалидный gzip)"
                return 1
            fi
        else
            log_error "Бэкап пустой"
            return 1
        fi
    else
        log_error "Файл бэкапа не найден"
        return 1
    fi
}

# Генерация отчета
generate_report() {
    local backup_file="$1"
    local media_backup="$2"
    local start_time="$3"
    local end_time="$4"
    
    local duration=$((end_time - start_time))
    local backup_size=$(du -h "$backup_file" 2>/dev/null | cut -f1 || echo "N/A")
    local media_size=$(du -h "$media_backup" 2>/dev/null | cut -f1 || echo "N/A")
    local total_backups=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f | wc -l)
    
    local report="📊 *Отчет о бэкапе Alekhin Clinic*

🕐 Время: $(date '+%Y-%m-%d %H:%M:%S')
⏱ Длительность: ${duration}с
📁 База данных: ${backup_size}
🖼 Медиафайлы: ${media_size}
📦 Всего бэкапов: ${total_backups}
✅ Статус: Успешно"

    echo "$report"
    
    # Отправка уведомлений
    send_telegram_notification "$report"
    send_email_notification "Бэкап Alekhin Clinic - Успешно" "$report"
}

# ===========================================
# ОСНОВНАЯ ФУНКЦИЯ
# ===========================================

main() {
    local start_time=$(date +%s)
    
    log_info "🚀 Запуск автобэкапа Alekhin Clinic"
    log_info "========================================"
    
    # Установка переменной окружения для пароля
    export PGPASSWORD="$DB_PASSWORD"
    
    # Создание директории
    create_backup_dir
    
    # Проверки
    check_database
    
    # Создание бэкапов
    local backup_file=$(create_backup)
    local media_backup=$(backup_media)
    
    # Проверка целостности
    if verify_backup "$backup_file"; then
        log_success "Бэкап создан и проверен успешно"
    else
        log_error "Ошибка проверки целостности бэкапа"
        exit 1
    fi
    
    # Очистка старых бэкапов
    cleanup_old_backups
    
    local end_time=$(date +%s)
    
    # Генерация отчета
    generate_report "$backup_file" "$media_backup" "$start_time" "$end_time"
    
    log_success "🎉 Автобэкап завершен успешно!"
}

# ===========================================
# ЗАПУСК
# ===========================================

# Проверка аргументов
case "${1:-}" in
    --verify)
        if [ -n "$2" ]; then
            verify_backup "$2"
        else
            echo "Использование: $0 --verify <путь_к_файлу>"
            exit 1
        fi
        ;;
    --cleanup)
        create_backup_dir
        cleanup_old_backups
        ;;
    --help)
        echo "Использование: $0 [опция]"
        echo ""
        echo "Опции:"
        echo "  (без опций)  Создать полный бэкап"
        echo "  --verify     Проверить целостность бэкапа"
        echo "  --cleanup    Очистить старые бэкапы"
        echo "  --help       Показать эту справку"
        ;;
    *)
        main
        ;;
esac