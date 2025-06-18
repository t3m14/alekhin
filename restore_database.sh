#!/bin/bash
# restore_database.sh
# Восстановление базы данных из бэкапа

set -e

# ===========================================
# КОНФИГУРАЦИЯ
# ===========================================

DB_NAME="postgres"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_HOST="localhost"
DB_PORT="5432"
DB_CONTAINER="backend"
BACKUP_DIR="/backups"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ===========================================
# ФУНКЦИИ
# ===========================================

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

# Показать доступные бэкапы
list_backups() {
    log_info "Доступные бэкапы в $BACKUP_DIR:"
    echo "================================================"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Директория бэкапов не найдена: $BACKUP_DIR"
        exit 1
    fi
    
    local backups=($(find "$BACKUP_DIR" -name "*.sql.gz" -type f -printf '%T@ %p\n' | sort -nr))
    
    if [ ${#backups[@]} -eq 0 ]; then
        log_warning "Бэкапы не найдены в $BACKUP_DIR"
        exit 1
    fi
    
    local i=1
    for backup in "${backups[@]}"; do
        local timestamp=$(echo "$backup" | cut -d' ' -f1)
        local filepath=$(echo "$backup" | cut -d' ' -f2-)
        local filename=$(basename "$filepath")
        local size=$(du -h "$filepath" | cut -f1)
        local date=$(date -d "@${timestamp%.*}" '+%Y-%m-%d %H:%M:%S')
        
        printf "%2d) %s (%s) - %s\n" "$i" "$filename" "$size" "$date"
        ((i++))
    done
    
    echo "================================================"
}

# Выбор бэкапа
select_backup() {
    local backups=($(find "$BACKUP_DIR" -name "*.sql.gz" -type f -printf '%T@ %p\n' | sort -nr | cut -d' ' -f2-))
    
    echo ""
    read -p "Введите номер бэкапа для восстановления (1-${#backups[@]}): " choice
    
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#backups[@]} ]; then
        echo "${backups[$((choice-1))]}"
    else
        log_error "Неверный выбор!"
        exit 1
    fi
}

# Подтверждение операции
confirm_restore() {
    local backup_file="$1"
    
    log_warning "⚠️  ВНИМАНИЕ! Это действие полностью заменит текущую базу данных!"
    log_warning "База данных: $DB_NAME"
    log_warning "Файл бэкапа: $(basename "$backup_file")"
    echo ""
    
    read -p "Вы уверены, что хотите продолжить? (yes/no): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        log_info "Операция отменена пользователем"
        exit 0
    fi
}

# Создание бэкапа перед восстановлением
create_safety_backup() {
    log_info "Создание резервного бэкапа перед восстановлением..."
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local safety_backup="$BACKUP_DIR/safety_backup_before_restore_${timestamp}.sql.gz"
    
    export PGPASSWORD="$DB_PASSWORD"
    
    if docker exec "$DB_CONTAINER" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --no-password \
        --clean \
        --if-exists \
        --create | gzip > "$safety_backup"; then
        
        log_success "Резервный бэкап создан: $(basename "$safety_backup")"
        echo "$safety_backup"
    else
        log_error "Ошибка создания резервного бэкапа!"
        exit 1
    fi
}

# Остановка приложения
stop_application() {
    log_info "Остановка приложения..."
    
    # Проверяем, запущен ли контейнер с приложением
    if docker ps -q -f name="$DB_CONTAINER" > /dev/null; then
        # Останавливаем только Django приложение, но не базу данных
        docker exec "$DB_CONTAINER" pkill -f "python.*manage.py.*runserver" || true
        log_success "Приложение остановлено"
    else
        log_warning "Контейнер приложения не найден или не запущен"
    fi
}

# Запуск приложения
start_application() {
    log_info "Запуск приложения..."
    
    # Перезапускаем контейнер с приложением
    if docker ps -a -q -f name="$DB_CONTAINER" > /dev/null; then
        docker restart "$DB_CONTAINER" > /dev/null 2>&1
        sleep 5  # Ждем запуска
        log_success "Приложение запущено"
    else
        log_warning "Контейнер не найден для перезапуска"
    fi
}

# Восстановление базы данных
restore_database() {
    local backup_file="$1"
    
    log_info "Начинаем восстановление базы данных..."
    log_info "Файл: $(basename "$backup_file")"
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Проверяем, что файл существует
    if [ ! -f "$backup_file" ]; then
        log_error "Файл бэкапа не найден: $backup_file"
        exit 1
    fi
    
    # Проверяем целостность архива
    if ! gzip -t "$backup_file"; then
        log_error "Файл бэкапа поврежден!"
        exit 1
    fi
    
    # Восстанавливаем базу данных
    log_info "Восстановление данных..."
    
    if zcat "$backup_file" | docker exec -i "$DB_CONTAINER" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d postgres \
        --quiet > /dev/null 2>&1; then
        
        log_success "База данных восстановлена успешно!"
    else
        log_error "Ошибка восстановления базы данных!"
        return 1
    fi
}

# Восстановление медиафайлов
restore_media() {
    local media_backup="$1"
    local media_dir="./media"
    
    if [ -f "$media_backup" ]; then
        log_info "Восстановление медиафайлов..."
        
        # Создаем резервную копию текущих медиафайлов
        if [ -d "$media_dir" ]; then
            local timestamp=$(date '+%Y%m%d_%H%M%S')
            mv "$media_dir" "${media_dir}_backup_${timestamp}"
            log_info "Текущие медиафайлы сохранены как ${media_dir}_backup_${timestamp}"
        fi
        
        # Восстанавливаем медиафайлы
        if tar -xzf "$media_backup" -C "$(dirname "$media_dir")"; then
            log_success "Медиафайлы восстановлены"
        else
            log_error "Ошибка восстановления медиафайлов"
        fi
    else
        log_warning "Бэкап медиафайлов не найден: $media_backup"
    fi
}

# Проверка восстановления
verify_restore() {
    log_info "Проверка восстановленной базы данных..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Проверяем подключение к базе
    if docker exec "$DB_CONTAINER" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -c "SELECT 1;" > /dev/null 2>&1; then
        
        log_success "Подключение к базе данных работает"
    else
        log_error "Не удается подключиться к восстановленной базе!"
        return 1
    fi
    
    # Проверяем наличие основных таблиц
    local tables=$(docker exec "$DB_CONTAINER" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ "$tables" -gt 0 ]; then
        log_success "Найдено $tables таблиц в базе данных"
    else
        log_error "Таблицы не найдены в восстановленной базе!"
        return 1
    fi
    
    # Проверяем миграции Django
    if docker exec "$DB_CONTAINER" python manage.py showmigrations --plan > /dev/null 2>&1; then
        log_success "Миграции Django в порядке"
    else
        log_warning "Проблемы с миграциями Django - может потребоваться ручная проверка"
    fi
}

# Поиск бэкапа медиафайлов по дате
find_media_backup() {
    local db_backup="$1"
    local db_timestamp=$(basename "$db_backup" | sed 's/.*_\([0-9]\{8\}_[0-9]\{6\}\).*/\1/')
    
    # Ищем медиа бэкап с той же датой
    local media_backup=$(find "$BACKUP_DIR" -name "media_backup_${db_timestamp}.tar.gz" -type f)
    
    if [ -n "$media_backup" ]; then
        echo "$media_backup"
    else
        # Ищем ближайший по времени медиа бэкап
        local closest_media=$(find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -type f -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)
        if [ -n "$closest_media" ]; then
            log_warning "Точное соответствие медиа бэкапа не найдено, используем: $(basename "$closest_media")"
            echo "$closest_media"
        fi
    fi
}

# Показать информацию о бэкапе
show_backup_info() {
    local backup_file="$1"
    
    log_info "Информация о бэкапе:"
    echo "===================="
    echo "Файл: $(basename "$backup_file")"
    echo "Размер: $(du -h "$backup_file" | cut -f1)"
    echo "Дата создания: $(date -r "$backup_file" '+%Y-%m-%d %H:%M:%S')"
    
    # Проверяем содержимое бэкапа
    log_info "Проверка содержимого бэкапа..."
    local tables_count=$(zcat "$backup_file" | grep -c "CREATE TABLE" || echo "0")
    echo "Количество таблиц: $tables_count"
    
    # Показываем первые несколько строк для проверки
    echo ""
    echo "Первые строки бэкапа:"
    echo "--------------------"
    zcat "$backup_file" | head -20
    echo "--------------------"
}

# ===========================================
# ГЛАВНАЯ ФУНКЦИЯ
# ===========================================

main() {
    log_info "🔄 Утилита восстановления базы данных Alekhin Clinic"
    log_info "===================================================="
    
    # Проверяем, что Docker запущен
    if ! docker ps > /dev/null 2>&1; then
        log_error "Docker не запущен или недоступен!"
        exit 1
    fi
    
    # Проверяем наличие контейнера базы данных
    if ! docker ps -f name="$DB_CONTAINER" --format "table {{.Names}}" | grep -q "$DB_CONTAINER"; then
        log_error "Контейнер $DB_CONTAINER не запущен!"
        log_info "Запустите контейнеры: docker-compose up -d"
        exit 1
    fi
    
    # Показываем доступные бэкапы
    list_backups
    
    # Пользователь выбирает бэкап
    local backup_file=$(select_backup)
    
    # Показываем информацию о выбранном бэкапе
    show_backup_info "$backup_file"
    
    # Подтверждение
    confirm_restore "$backup_file"
    
    # Создаем резервный бэкап
    local safety_backup=$(create_safety_backup)
    
    # Ищем соответствующий медиа бэкап
    local media_backup=$(find_media_backup "$backup_file")
    
    # Останавливаем приложение
    stop_application
    
    # Восстанавливаем базу данных
    if restore_database "$backup_file"; then
        log_success "База данных восстановлена!"
        
        # Восстанавливаем медиафайлы если есть
        if [ -n "$media_backup" ]; then
            restore_media "$media_backup"
        fi
        
        # Запускаем приложение
        start_application
        
        # Проверяем восстановление
        if verify_restore; then
            log_success "🎉 Восстановление завершено успешно!"
            log_info "Резервный бэкап сохранен как: $(basename "$safety_backup")"
        else
            log_error "Восстановление завершилось с ошибками!"
            exit 1
        fi
    else
        log_error "Ошибка восстановления базы данных!"
        log_info "Запускаем приложение обратно..."
        start_application
        exit 1
    fi
}

# ===========================================
# ОБРАБОТКА АРГУМЕНТОВ
# ===========================================

case "${1:-}" in
    --list)
        list_backups
        ;;
    --info)
        if [ -n "$2" ]; then
            show_backup_info "$2"
        else
            echo "Использование: $0 --info <путь_к_файлу>"
            exit 1
        fi
        ;;
    --auto)
        if [ -n "$2" ]; then
            # Автоматическое восстановление без интерактивности
            backup_file="$2"
            if [ ! -f "$backup_file" ]; then
                log_error "Файл не найден: $backup_file"
                exit 1
            fi
            
            log_info "Автоматическое восстановление: $(basename "$backup_file")"
            safety_backup=$(create_safety_backup)
            media_backup=$(find_media_backup "$backup_file")
            
            stop_application
            restore_database "$backup_file"
            
            if [ -n "$media_backup" ]; then
                restore_media "$media_backup"
            fi
            
            start_application
            verify_restore
        else
            echo "Использование: $0 --auto <путь_к_файлу>"
            exit 1
        fi
        ;;
    --help)
        echo "Утилита восстановления базы данных Alekhin Clinic"
        echo ""
        echo "Использование: $0 [опция] [файл]"
        echo ""
        echo "Опции:"
        echo "  (без опций)     Интерактивное восстановление"
        echo "  --list          Показать доступные бэкапы"
        echo "  --info <файл>   Показать информацию о бэкапе"
        echo "  --auto <файл>   Автоматическое восстановление"
        echo "  --help          Показать эту справку"
        echo ""
        echo "Примеры:"
        echo "  $0"
        echo "  $0 --list"
        echo "  $0 --info /backups/backup_20231215_020000.sql.gz"
        echo "  $0 --auto /backups/backup_20231215_020000.sql.gz"
        ;;
    *)
        main
        ;;
esac