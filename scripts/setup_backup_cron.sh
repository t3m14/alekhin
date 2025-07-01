#!/bin/bash

PROJECT_DIR="$(pwd)"
SCRIPT_PATH="$PROJECT_DIR/scripts/backup.sh"

echo "=== Setting up PostgreSQL Backup Cron Jobs ==="
echo "Project directory: $PROJECT_DIR"

# Проверка существования скрипта
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "✗ Backup script not found: $SCRIPT_PATH"
    echo "Please ensure scripts/backup.sh exists and is executable"
    exit 1
fi

# Сделать скрипт исполняемым
chmod +x "$SCRIPT_PATH"

# Создать временный файл crontab
TEMP_CRON=$(mktemp)

# Получить существующий crontab (если есть)
crontab -l 2>/dev/null > "$TEMP_CRON" || true

# Удалить существующие задания PostgreSQL бекапов
grep -v "postgres.*backup" "$TEMP_CRON" > "${TEMP_CRON}.tmp" && mv "${TEMP_CRON}.tmp" "$TEMP_CRON"

echo "Adding backup schedules to crontab..."

# Добавить новые задания
cat >> "$TEMP_CRON" << EOF

# PostgreSQL Automatic Backups
# Daily full backup at 2:00 AM
0 2 * * * cd $PROJECT_DIR && $SCRIPT_PATH >> /var/log/postgres_backup.log 2>&1

# Quick backup every 6 hours
0 */6 * * * cd $PROJECT_DIR && docker exec postgres_db pg_dump -Fc -U postgres postgres > $PROJECT_DIR/backups/quick_\$(date +\%Y\%m\%d_\%H\%M).backup

# Weekly cleanup of old logs (Sundays at 3:00 AM)
0 3 * * 0 find $PROJECT_DIR/logs -name "*.log" -mtime +30 -delete

# Monthly disk space check (1st of month at 1:00 AM)
0 1 1 * * df -h $PROJECT_DIR && du -sh $PROJECT_DIR/backups/

EOF

# Установить новый crontab
crontab "$TEMP_CRON"

# Удалить временный файл
rm "$TEMP_CRON"

echo "✓ Cron jobs installed successfully"

echo ""
echo "=== Scheduled Backup Tasks ==="
echo "📅 Daily full backup: 2:00 AM"
echo "⚡ Quick backup: Every 6 hours"
echo "🧹 Log cleanup: Weekly (Sunday 3:00 AM)"
echo "💾 Disk check: Monthly (1st day 1:00 AM)"

echo ""
echo "=== View Current Crontab ==="
crontab -l | grep -A 10 -B 2 "PostgreSQL"

echo ""
echo "=== Manual Commands ==="
echo "View cron logs: sudo tail -f /var/log/cron"
echo "View backup logs: tail -f $PROJECT_DIR/logs/backup_\$(date +%Y%m).log"
echo "Test backup now: $SCRIPT_PATH"

echo ""
echo "=== Setup Complete ==="
echo "Your backups will run automatically!"
echo "First backup will occur at next 2:00 AM or run manually now."

# Предложить запустить тестовый бекап
read -p "Run test backup now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running test backup..."
    "$SCRIPT_PATH"
fi