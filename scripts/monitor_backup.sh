#!/bin/bash

BACKUP_DIR="./backups"
LOG_DIR="./logs"

echo "=== PostgreSQL Backup System Status Report ==="
echo "Generated at: $(date)"
echo "Report by: $(whoami)@$(hostname)"
echo

# Цветные коды для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция цветного вывода
color_echo() {
    echo -e "${2}${1}${NC}"
}

# Проверка статуса контейнеров
echo "--- Container Status ---"
CONTAINERS=("postgres_db" "postgres_backup" "pgadmin")
for container in "${CONTAINERS[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        color_echo "✓ $container: Running" "$GREEN"
        # Показать время запуска
        STARTED=$(docker inspect --format='{{.State.StartedAt}}' "$container" | cut -d'T' -f1,2 | tr 'T' ' ')
        echo "  Started: $STARTED"
    else
        color_echo "✗ $container: Not running" "$RED"
    fi
done
echo

# Проверка доступности базы данных
echo "--- Database Connectivity ---"
if docker exec postgres_db pg_isready -U postgres >/dev/null 2>&1; then
    color_echo "✓ PostgreSQL: Accessible" "$GREEN"
    
    # Информация о базе данных
    DB_INFO=$(docker exec postgres_db psql -U postgres -d postgres -t -c "
    SELECT 
        'Version: ' || version() || E'\n' ||
        'Size: ' || pg_size_pretty(pg_database_size('postgres')) || E'\n' ||
        'Tables: ' || (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') || E'\n' ||
        'Active connections: ' || (SELECT count(*) FROM pg_stat_activity WHERE state = 'active')
    " 2>/dev/null | head -4)
    
    echo "$DB_INFO"
else
    color_echo "✗ PostgreSQL: Not accessible" "$RED"
fi
echo

# Проверка доступности pgAdmin
echo "--- pgAdmin Status ---"
if curl -s http://localhost:5050 >/dev/null 2>&1; then
    color_echo "✓ pgAdmin: Accessible at http://localhost:5050" "$GREEN"
else
    color_echo "✗ pgAdmin: Not accessible" "$RED"
fi
echo

# Анализ бекапов
echo "--- Backup Analysis ---"
if [ -d "$BACKUP_DIR" ]; then
    TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.backup" | wc -l)
    TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
    
    echo "Total backups: $TOTAL_BACKUPS files"
    echo "Total size: $TOTAL_SIZE"
    echo
    
    # Последние бекапы
    echo "Recent backups (last 10):"
    find "$BACKUP_DIR" -name "postgres_*.sql.gz" -o -name "postgres_*.backup" -o -name "auto_postgres_*.sql.gz" | 
    sort -r | head -10 | while read backup; do
        SIZE=$(stat -c%s "$backup" 2>/dev/null | awk '{print int($1/1024/1024)"M"}')
        DATE=$(stat -c%y "$backup" | cut -d' ' -f1,2 | cut -d'.' -f1)
        echo "  $(basename "$backup") - $SIZE - $DATE"
    done
    
    # Проверка на старые бекапы
    echo
    OLD_BACKUPS=$(find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.backup" -mtime +7 | wc -l)
    if [ "$OLD_BACKUPS" -gt 0 ]; then
        color_echo "⚠️  Warning: $OLD_BACKUPS backup(s) older than 7 days found" "$YELLOW"
    else
        color_echo "✓ No old backups found (cleanup working correctly)" "$GREEN"
    fi
    
    # Проверка последнего автоматического бекапа
    echo
    LAST_AUTO_BACKUP=$(find "$BACKUP_DIR" -name "auto_postgres_backup_*.sql.gz" | sort -r | head -1)
    if [ -n "$LAST_AUTO_BACKUP" ]; then
        LAST_BACKUP_TIME=$(stat -c%Y "$LAST_AUTO_BACKUP")
        CURRENT_TIME=$(date +%s)
        HOURS_AGO=$(( (CURRENT_TIME - LAST_BACKUP_TIME) / 3600 ))
        
        if [ $HOURS_AGO -lt 25 ]; then
            color_echo "✓ Last automatic backup: $HOURS_AGO hours ago" "$GREEN"
        else
            color_echo "⚠️  Last automatic backup: $HOURS_AGO hours ago (check backup service)" "$YELLOW"
        fi
    else
        color_echo "⚠️  No automatic backups found" "$YELLOW"
    fi
else
    color_echo "✗ Backup directory not found: $BACKUP_DIR" "$RED"
fi
echo

# Проверка логов
echo "--- Log Analysis ---"
if [ -d "$LOG_DIR" ]; then
    RECENT_LOGS=$(find "$LOG_DIR" -name "*.log" -mtime -7 | wc -l)
    echo "Recent log files (last 7 days): $RECENT_LOGS"
    
    # Последние ошибки в логах
    if [ $RECENT_LOGS -gt 0 ]; then
        echo "Recent errors:"
        find "$LOG_DIR" -name "*.log" -mtime -7 -exec grep -l "✗\|ERROR\|FAIL" {} \; 2>/dev/null | head -3 | while read logfile; do
            echo "  $(basename "$logfile"):"
            grep "✗\|ERROR\|FAIL" "$logfile" | tail -2 | sed 's/^/    /'
        done
    fi
else
    color_echo "⚠️  Log directory not found: $LOG_DIR" "$YELLOW"
fi
echo

# Проверка дискового пространства
echo "--- Disk Usage ---"
DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    color_echo "⚠️  Warning: Disk usage is ${DISK_USAGE}%" "$YELLOW"
elif [ "$DISK_USAGE" -gt 90 ]; then
    color_echo "✗ Critical: Disk usage is ${DISK_USAGE}%" "$RED"
else
    color_echo "✓ Disk usage: ${DISK_USAGE}%" "$GREEN"
fi

echo "Current directory usage:"
du -sh "$BACKUP_DIR" "$LOG_DIR" . 2>/dev/null | sort -hr
echo

# Рекомендации
echo "--- Recommendations ---"
if [ "$OLD_BACKUPS" -gt 0 ]; then
    echo "• Run cleanup script to remove old backups"
fi

if [ $HOURS_AGO -gt 25 ] 2>/dev/null; then
    echo "• Check backup service status: docker logs postgres_backup"
fi

if [ "$DISK_USAGE" -gt 80 ]; then
    echo "• Consider cleaning old backups or expanding disk space"
fi

if ! curl -s http://localhost:5050 >/dev/null 2>&1; then
    echo "• Check pgAdmin service: docker logs pgadmin"
fi

echo
echo "=== End of Report ==="
echo "To get detailed logs: tail -f $LOG_DIR/backup_$(date +%Y%m).log"
echo "To create manual backup: ./scripts/backup.sh"
echo "To access pgAdmin: http://localhost:5050 (admin@admin.com / admin123)"
