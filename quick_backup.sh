#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="./backups/quick_backup_${TIMESTAMP}.sql"
mkdir -p ./backups

echo "Creating backup..."
if docker exec -t postgres_db pg_dump -U postgres postgres > "$BACKUP_FILE"; then
    gzip "$BACKUP_FILE"
    SIZE=$(stat -c%s "${BACKUP_FILE}.gz")
    echo "✓ Backup created: $(basename "${BACKUP_FILE}.gz") ($(($SIZE / 1024 / 1024)) MB)"
else
    echo "✗ Backup failed"
    rm -f "$BACKUP_FILE"
fi
