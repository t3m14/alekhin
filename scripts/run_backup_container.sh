#!/bin/bash
set -e

BACKUP_CONTAINER_NAME="postgres_backup"
NETWORK_NAME="$(basename $(pwd))_default"

echo "Starting backup container..."

# Остановка существующего контейнера
docker stop "$BACKUP_CONTAINER_NAME" 2>/dev/null || true
docker rm "$BACKUP_CONTAINER_NAME" 2>/dev/null || true

mkdir -p ./backups

# Запуск контейнера бекапов
docker run -d \
  --name "$BACKUP_CONTAINER_NAME" \
  --network "$NETWORK_NAME" \
  --restart unless-stopped \
  -e PGPASSWORD=S3cUr3P@ssw0rd_2025! \
  -v "$(pwd)/backups:/backups" \
  postgres:14 \
  bash -c 'while true; do
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="/backups/auto_backup_${timestamp}.sql"
    echo "[$(date)] Creating backup: $backup_file"
    if pg_dump -h postgres_db -U postgres postgres > $backup_file; then
      gzip $backup_file
      echo "[$(date)] ✓ Backup completed: ${backup_file}.gz"
    else
      echo "[$(date)] ✗ Backup failed"
      rm -f $backup_file
    fi
    find /backups -name "auto_backup_*.sql.gz" -mtime +7 -delete
    sleep 86400
  done'

echo "✓ Backup container started: $BACKUP_CONTAINER_NAME"
