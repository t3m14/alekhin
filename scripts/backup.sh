#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
CONTAINER_NAME="postgres_db"
DB_USER="postgres"
DB_NAME="postgres"

echo "=== PostgreSQL Backup Script ==="
echo "Starting backup at: $(date)"

# Создание директории для бекапов
mkdir -p "$BACKUP_DIR"

# Проверка доступности контейнера
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✗ PostgreSQL container is not running"
    exit 1
fi

# Проверка подключения к базе
echo "Checking database connection..."
if ! docker exec "$CONTAINER_NAME" pg_isready -U "$DB_USER" > /dev/null 2>&1; then
    echo "✗ Database is not ready"
    exit 1
fi
echo "✓ Database connection OK"

# Создание полного бекапа
backup_file="$BACKUP_DIR/postgres_full_${TIMESTAMP}.sql"
echo "Creating full backup: $(basename "$backup_file")"

if docker exec -t "$CONTAINER_NAME" pg_dump -c -U "$DB_USER" "$DB_NAME" > "$backup_file"; then
    echo "✓ Backup created successfully"
    gzip "$backup_file"
    size=$(stat -c%s "${backup_file}.gz")
    echo "✓ Backup compressed: $(basename "${backup_file}.gz") ($(($size / 1024 / 1024)) MB)"
else
    echo "✗ Backup failed"
    rm -f "$backup_file"
    exit 1
fi

# Очистка старых бекапов
find "$BACKUP_DIR" -name "postgres_*.sql.gz" -mtime +7 -delete

echo "=== Backup completed at: $(date) ==="
