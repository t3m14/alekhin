#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="./backups/quick_backup_${TIMESTAMP}.sql"
CONTAINER_NAME="postgres_db"
DB_USER="postgres"
DB_NAME="postgres"

echo "=== Quick PostgreSQL Backup ==="
echo "Starting at: $(date)"

mkdir -p ./backups

if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✗ PostgreSQL container is not running"
    exit 1
fi

echo "Creating quick backup..."
if docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"; then
    gzip "$BACKUP_FILE"
    SIZE=$(stat -c%s "${BACKUP_FILE}.gz")
    echo "✓ Quick backup created: $(basename "${BACKUP_FILE}.gz")"
    echo "✓ Size: $(($SIZE / 1024 / 1024)) MB"
else
    echo "✗ Quick backup failed"
    exit 1
fi

echo "=== Quick backup completed ==="
