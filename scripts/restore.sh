#!/bin/bash
set -e

# Функция для отображения использования
show_usage() {
    echo "Usage: $0 [OPTIONS] <backup_file>"
    echo ""
    echo "Options:"
    echo "  -t, --test-only    Test restore without affecting production data"
    echo "  -f, --force        Skip confirmation prompts"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Available backups:"
    ls -la ./backups/postgres_*.{sql.gz,backup} 2>/dev/null | head -10 || echo "No PostgreSQL backups found"
    echo ""
    echo "Examples:"
    echo "  $0 ./backups/postgres_full_20250701_120000.sql.gz"
    echo "  $0 --test-only ./backups/postgres_custom_20250701_120000.backup"
}

# Параметры по умолчанию
TEST_ONLY=false
FORCE=false
BACKUP_FILE=""

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--test-only)
            TEST_ONLY=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            BACKUP_FILE="$1"
            shift
            ;;
    esac
done

if [ -z "$BACKUP_FILE" ]; then
    echo "Error: No backup file specified"
    show_usage
    exit 1
fi

# Конфигурация
CONTAINER_NAME="postgres_db"
DB_USER="postgres"
DB_NAME="postgres"
TEST_DB="postgres_restore_test"
LOG_FILE="./logs/restore_$(date +%Y%m%d_%H%M%S).log"

# Функция логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Проверка файла бекапа
if [ ! -f "$BACKUP_FILE" ]; then
    log "✗ Backup file not found: $BACKUP_FILE"
    exit 1
fi

log "=== PostgreSQL Restore Script Started ==="
log "Backup file: $BACKUP_FILE"
log "Test mode: $TEST_ONLY"

# Создание директории для логов
mkdir -p "$(dirname "$LOG_FILE")"

# Проверка доступности контейнера
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    log "✗ PostgreSQL container is not running"
    exit 1
fi

# Проверка подключения к базе
log "Checking database connection..."
if ! docker exec "$CONTAINER_NAME" pg_isready -U "$DB_USER" > /dev/null 2>&1; then
    log "✗ Database is not ready"
    exit 1
fi
log "✓ Database connection OK"

# Функция подтверждения
confirm() {
    if [ "$FORCE" = true ]; then
        return 0
    fi
    
    echo -n "$1 (y/N): "
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Создание резервной копии текущей базы (если не тестовый режим)
if [ "$TEST_ONLY" = false ]; then
    log "--- Creating current database backup ---"
    CURRENT_BACKUP="./backups/before_restore_$(date +%Y%m%d_%H%M%S).sql"
    if docker exec -t "$CONTAINER_NAME" pg_dump -c -U "$DB_USER" "$DB_NAME" > "$CURRENT_BACKUP"; then
        gzip "$CURRENT_BACKUP"
        log "✓ Current database backed up to: $(basename "${CURRENT_BACKUP}.gz")"
    else
        log "✗ Failed to create current database backup"
        if ! confirm "Continue without current backup?"; then
            exit 1
        fi
    fi
fi

# Выбор целевой базы данных
TARGET_DB="$DB_NAME"
if [ "$TEST_ONLY" = true ]; then
    TARGET_DB="$TEST_DB"
    log "--- Creating test database ---"
    docker exec "$CONTAINER_NAME" dropdb -U "$DB_USER" "$TEST_DB" 2>/dev/null || true
    docker exec "$CONTAINER_NAME" createdb -U "$DB_USER" "$TEST_DB"
    log "✓ Test database created: $TEST_DB"
fi

# Подтверждение восстановления
if [ "$TEST_ONLY" = false ]; then
    log "⚠️  WARNING: This will restore the production database!"
    if ! confirm "Are you sure you want to continue?"; then
        log "Restore cancelled by user"
        exit 0
    fi
    
    # Остановка приложения
    log "--- Stopping application services ---"
    docker-compose stop backend admin frontend
    log "✓ Application services stopped"
fi

# Функция восстановления из SQL файла
restore_from_sql() {
    local file="$1"
    local target_db="$2"
    log "Restoring from SQL file to database: $target_db"
    
    if [[ "$file" == *.gz ]]; then
        log "Decompressing and restoring..."
        if gunzip -c "$file" | docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$target_db"; then
            log "✓ SQL restore completed successfully"
            return 0
        else
            log "✗ SQL restore failed"
            return 1
        fi
    else
        log "Restoring uncompressed SQL..."
        if docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$target_db" < "$file"; then
            log "✓ SQL restore completed successfully"
            return 0
        else
            log "✗ SQL restore failed"
            return 1
        fi
    fi
}

# Функция восстановления из custom формата
restore_from_custom() {
    local file="$1"
    local target_db="$2"
    log "Restoring from custom format to database: $target_db"
    
    if docker exec -i "$CONTAINER_NAME" pg_restore -U "$DB_USER" -d "$target_db" -c --if-exists < "$file"; then
        log "✓ Custom restore completed successfully"
        return 0
    else
        log "✗ Custom restore failed"
        return 1
    fi
}

# Определение типа файла и восстановление
log "--- Starting restore process ---"
RESTORE_SUCCESS=false

if [[ "$BACKUP_FILE" == *.backup ]]; then
    if restore_from_custom "$BACKUP_FILE" "$TARGET_DB"; then
        RESTORE_SUCCESS=true
    fi
elif [[ "$BACKUP_FILE" == *.sql ]] || [[ "$BACKUP_FILE" == *.sql.gz ]]; then
    if restore_from_sql "$BACKUP_FILE" "$TARGET_DB"; then
        RESTORE_SUCCESS=true
    fi
else
    log "✗ Unsupported backup file format: $BACKUP_FILE"
    exit 1
fi

if [ "$RESTORE_SUCCESS" = false ]; then
    log "✗ Restore failed"
    if [ "$TEST_ONLY" = false ]; then
        log "--- Starting application services ---"
        docker-compose start backend admin frontend
    fi
    exit 1
fi

# Проверка восстановления
log "--- Verifying restore ---"
VERIFY_RESULT=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$TARGET_DB" -t -c "
SELECT 
    'Size: ' || pg_size_pretty(pg_database_size('$TARGET_DB')) || 
    ', Tables: ' || (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public')
" | xargs)
log "Restored database info: $VERIFY_RESULT"

# Тест подключения к восстановленной базе
log "Testing database connectivity..."
if docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$TARGET_DB" -c "SELECT 1;" > /dev/null 2>&1; then
    log "✓ Database connectivity test passed"
else
    log "✗ Database connectivity test failed"
    RESTORE_SUCCESS=false
fi

# Завершение для тестового режима
if [ "$TEST_ONLY" = true ]; then
    log "=== Test restore completed ==="
    log "Test database '$TEST_DB' contains the restored data"
    log "To clean up test database: docker exec $CONTAINER_NAME dropdb -U $DB_USER $TEST_DB"
    exit 0
fi

# Запуск приложения (только для продакшн режима)
if [ "$RESTORE_SUCCESS" = true ]; then
    log "--- Starting application services ---"
    docker-compose start backend admin frontend
    
    # Ожидание запуска сервисов
    log "Waiting for services to start..."
    sleep 10
    
    # Проверка статуса сервисов
    log "--- Service Status ---"
    docker-compose ps | grep -E "(backend|admin|frontend)" | while read line; do
        log "Service status: $line"
    done
    
    log "=== Restore completed successfully ==="
    log "Application should be available at:"
    log "  - Backend: http://localhost:8000"
    log "  - Admin: http://localhost:3001"  
    log "  - Frontend: http://localhost:3002"
else
    log "✗ Restore verification failed"
    exit 1
fi
