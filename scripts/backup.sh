#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
CONTAINER_NAME="postgres_db"
DB_USER="postgres"
DB_NAME="postgres"
LOG_FILE="./logs/backup_$(date +%Y%m).log"

# Функция логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== PostgreSQL Backup Script Started ==="

# Создание директорий
mkdir -p "$BACKUP_DIR" "$(dirname "$LOG_FILE")"

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

# 1. Custom формат (для pgAdmin Restore)
log "Creating custom format backup (for pgAdmin)..."
CUSTOM_BACKUP="$BACKUP_DIR/postgres_custom_${TIMESTAMP}.backup"
if docker exec -t "$CONTAINER_NAME" pg_dump -Fc -U "$DB_USER" "$DB_NAME" > "$CUSTOM_BACKUP"; then
    SIZE=$(stat -c%s "$CUSTOM_BACKUP")
    log "✓ Custom backup: $(basename "$CUSTOM_BACKUP") ($(($SIZE / 1024 / 1024)) MB)"
    
    # Копируем в pgAdmin для удобства
    if docker ps | grep -q pgadmin; then
        docker cp "$CUSTOM_BACKUP" pgladmin:/tmp/ 2>/dev/null || true
        log "✓ Copied to pgAdmin: /tmp/$(basename "$CUSTOM_BACKUP")"
    fi
else
    log "✗ Custom backup failed"
    rm -f "$CUSTOM_BACKUP"
fi

# 2. SQL формат (для Query Tool и командной строки)
log "Creating SQL format backup..."
SQL_BACKUP="$BACKUP_DIR/postgres_sql_${TIMESTAMP}.sql"
if docker exec -t "$CONTAINER_NAME" pg_dump -c -U "$DB_USER" "$DB_NAME" > "$SQL_BACKUP"; then
    log "✓ SQL backup created successfully"
    gzip "$SQL_BACKUP"
    SIZE=$(stat -c%s "${SQL_BACKUP}.gz")
    log "✓ SQL backup compressed: $(basename "${SQL_BACKUP}.gz") ($(($SIZE / 1024 / 1024)) MB)"
else
    log "✗ SQL backup failed"
    rm -f "$SQL_BACKUP"
fi

# 3. Только данные (для частичного восстановления)
log "Creating data-only backup..."
DATA_BACKUP="$BACKUP_DIR/postgres_data_${TIMESTAMP}.backup"
if docker exec -t "$CONTAINER_NAME" pg_dump -Fc -a -U "$DB_USER" "$DB_NAME" > "$DATA_BACKUP"; then
    SIZE=$(stat -c%s "$DATA_BACKUP")
    log "✓ Data-only backup: $(basename "$DATA_BACKUP") ($(($SIZE / 1024 / 1024)) MB)"
else
    log "✗ Data-only backup failed"
    rm -f "$DATA_BACKUP"
fi

# 4. Только схема (для структуры БД)
log "Creating schema-only backup..."
SCHEMA_BACKUP="$BACKUP_DIR/postgres_schema_${TIMESTAMP}.backup"
if docker exec -t "$CONTAINER_NAME" pg_dump -Fc -s -U "$DB_USER" "$DB_NAME" > "$SCHEMA_BACKUP"; then
    SIZE=$(stat -c%s "$SCHEMA_BACKUP")
    log "✓ Schema-only backup: $(basename "$SCHEMA_BACKUP") ($(($SIZE / 1024 / 1024)) MB)"
else
    log "✗ Schema-only backup failed"
    rm -f "$SCHEMA_BACKUP"
fi

# Информация о базе данных
log "--- Database Information ---"
DB_INFO=$(docker exec "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -t -c "
SELECT 
    'Size: ' || pg_size_pretty(pg_database_size('$DB_NAME')) || 
    ', Tables: ' || (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') ||
    ', Records: ' || (
        SELECT sum(n_tup_ins + n_tup_upd) 
        FROM pg_stat_user_tables
    )
" | xargs)
log "Database info: $DB_INFO"

# Очистка старых бекапов
log "--- Cleaning old backups ---"
OLD_COUNT=$(find "$BACKUP_DIR" -name "postgres_*.sql.gz" -o -name "postgres_*.backup" -mtime +7 | wc -l)
find "$BACKUP_DIR" -name "postgres_*.sql.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "postgres_*.backup" -mtime +7 -delete
if [ "$OLD_COUNT" -gt 0 ]; then
    log "✓ Cleaned $OLD_COUNT old backup file(s)"
fi

# Итоговая статистика
log "--- Backup Summary ---"
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)
log "Total backups: $BACKUP_COUNT files, $TOTAL_SIZE"

log "=== Backup completed successfully ==="

# Инструкции для использования
echo ""
echo "=== Usage Instructions ==="
echo "📁 Backup files created:"
ls -lah "$BACKUP_DIR" | grep "$TIMESTAMP" | while read line; do
    echo "  $line"
done

echo ""
echo "🔧 For pgAdmin Restore:"
echo "  1. Use: postgres_custom_${TIMESTAMP}.backup"
echo "  2. Path in pgAdmin: /tmp/postgres_custom_${TIMESTAMP}.backup"
echo "  3. Format: Custom or tar"

echo ""
echo "📝 For pgAdmin Query Tool:"
echo "  1. Unzip: gunzip postgres_sql_${TIMESTAMP}.sql.gz"
echo "  2. Open .sql file in Query Tool"

echo ""
echo "⚡ Quick restore test:"
echo "  ./scripts/restore.sh $CUSTOM_BACKUP"

# Отправка уведомления (если настроено)
if command -v mail >/dev/null 2>&1 && [ -n "$BACKUP_EMAIL" ]; then
    echo "Backup completed successfully at $(date). Total size: $TOTAL_SIZE" | \
    mail -s "PostgreSQL Backup Success - $(hostname)" "$BACKUP_EMAIL" 2>/dev/null || true
fi