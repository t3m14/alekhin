#!/bin/bash
# setup_backup_cron.sh
# Настройка автоматических бэкапов через cron

# ===========================================
# CRON ЗАДАЧИ ДЛЯ РАЗНЫХ СТРАТЕГИЙ
# ===========================================

echo "🕐 Настройка автоматических бэкапов через cron"
echo "=============================================="

# Создание cron файла
CRON_FILE="/tmp/alekhin_backup_cron"

cat > "$CRON_FILE" << 'EOF'
# Автоматические бэкапы для Alekhin Clinic
# Сгенерировано автоматически

# 1. ЕЖЕДНЕВНЫЙ БЭКАП в 2:00 ночи
0 2 * * * /opt/alekhin-clinic/scripts/backup_database.sh >> /var/log/alekhin_backup.log 2>&1

# 2. ЕЖЕНЕДЕЛЬНАЯ ОЧИСТКА в воскресенье в 3:00
0 3 * * 0 /opt/alekhin-clinic/scripts/backup_database.sh --cleanup >> /var/log/alekhin_backup.log 2>&1

# 3. ЕЖЕМЕСЯЧНАЯ ПРОВЕРКА ЦЕЛОСТНОСТИ (первое число каждого месяца в 4:00)
0 4 1 * * find /backups -name "*.sql.gz" -mtime -7 | head -1 | xargs -I {} /opt/alekhin-clinic/scripts/backup_database.sh --verify {} >> /var/log/alekhin_backup.log 2>&1

# 4. БЫСТРЫЙ БЭКАП КАЖДЫЕ 6 ЧАСОВ (для критически важных данных)
# 0 */6 * * * /opt/alekhin-clinic/scripts/backup_database.sh >> /var/log/alekhin_backup.log 2>&1

# 5. РОТАЦИЯ ЛОГОВ (каждую неделю)
0 1 * * 1 logrotate /etc/logrotate.d/alekhin_backup
EOF

echo "📝 Созданы следующие задачи cron:"
echo "================================"
cat "$CRON_FILE"

echo ""
echo "🔧 Для установки выполните:"
echo "sudo crontab -u root $CRON_FILE"

# ===========================================
# КОНФИГУРАЦИЯ LOGROTATE
# ===========================================

LOGROTATE_FILE="/tmp/alekhin_backup_logrotate"

cat > "$LOGROTATE_FILE" << 'EOF'
/var/log/alekhin_backup.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        # Отправка уведомления о ротации логов
        echo "Лог-файлы бэкапа Alekhin Clinic ротированы $(date)" | logger -t alekhin_backup
    endscript
}
EOF

echo ""
echo "📄 Конфигурация logrotate создана:"
echo "sudo cp $LOGROTATE_FILE /etc/logrotate.d/alekhin_backup"

# ===========================================
# SYSTEMD TIMER (АЛЬТЕРНАТИВА CRON)
# ===========================================

SYSTEMD_SERVICE="/tmp/alekhin-backup.service"
SYSTEMD_TIMER="/tmp/alekhin-backup.timer"

cat > "$SYSTEMD_SERVICE" << 'EOF'
[Unit]
Description=Alekhin Clinic Database Backup
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/opt/alekhin-clinic/scripts/backup_database.sh
User=root
Group=docker

# Переменные окружения
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=alekhin-backup

# Безопасность
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/backups /var/log

[Install]
WantedBy=multi-user.target
EOF

cat > "$SYSTEMD_TIMER" << 'EOF'
[Unit]
Description=Run Alekhin Clinic Backup Daily
Requires=alekhin-backup.service

[Timer]
# Запуск каждый день в 2:00
OnCalendar=daily
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF

echo ""
echo "⚙️  Файлы systemd timer созданы:"
echo "sudo cp $SYSTEMD_SERVICE /etc/systemd/system/"
echo "sudo cp $SYSTEMD_TIMER /etc/systemd/system/"
echo "sudo systemctl enable alekhin-backup.timer"
echo "sudo systemctl start alekhin-backup.timer"

# ===========================================
# DOCKER COMPOSE ИНТЕГРАЦИЯ
# ===========================================

DOCKER_BACKUP_SERVICE="/tmp/docker-compose.backup.yml"

cat > "$DOCKER_BACKUP_SERVICE" << 'EOF'
version: '3.8'

services:
  backup:
    image: postgres:14
    container_name: alekhin_backup
    environment:
      - PGPASSWORD=postgres
    volumes:
      - ./backups:/backups
      - ./scripts:/scripts
      - postgres_data:/var/lib/postgresql/data:ro
    networks:
      - default
    command: >
      sh -c "
        echo 'Запуск автоматического бэкапа...' &&
        pg_dump -h db -U postgres -d postgres --clean --if-exists --create > /backups/backup_$(date +%Y%m%d_%H%M%S).sql &&
        gzip /backups/backup_$(date +%Y%m%d_%H%M%S).sql &&
        echo 'Бэкап завершен!'
      "
    depends_on:
      - db
    profiles:
      - backup

volumes:
  postgres_data:
    external: true

networks:
  default:
    external:
      name: alekhin-clinic_default
EOF

echo ""
echo "🐳 Docker Compose сервис для бэкапа:"
echo "cp $DOCKER_BACKUP_SERVICE docker-compose.backup.yml"
echo "docker-compose -f docker-compose.backup.yml --profile backup up backup"

# ===========================================
# СКРИПТ МОНИТОРИНГА
# ===========================================

MONITOR_SCRIPT="/tmp/backup_monitor.sh"

cat > "$MONITOR_SCRIPT" << 'EOF'
#!/bin/bash
# backup_monitor.sh
# Мониторинг состояния бэкапов

BACKUP_DIR="/backups"
ALERT_EMAIL="admin@alekhin-clinic.com"
MAX_AGE_HOURS=26  # Максимальный возраст последнего бэкапа

# Проверка последнего бэкапа
latest_backup=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f -printf '%T@ %p\n' | sort -nr | head -1)

if [ -z "$latest_backup" ]; then
    echo "❌ КРИТИЧЕСКАЯ ОШИБКА: Бэкапы не найдены!"
    echo "Бэкапы отсутствуют в директории $BACKUP_DIR" | mail -s "КРИТИЧНО: Нет бэкапов Alekhin Clinic" "$ALERT_EMAIL"
    exit 1
fi

backup_time=$(echo "$latest_backup" | cut -d' ' -f1)
backup_file=$(echo "$latest_backup" | cut -d' ' -f2-)
current_time=$(date +%s)
age_hours=$(( (current_time - ${backup_time%.*}) / 3600 ))

echo "📊 Статус бэкапов Alekhin Clinic"
echo "================================"
echo "Последний бэкап: $(basename "$backup_file")"
echo "Возраст: $age_hours часов"
echo "Размер: $(du -h "$backup_file" | cut -f1)"

if [ "$age_hours" -gt "$MAX_AGE_HOURS" ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Бэкап устарел!"
    echo "Последний бэкап был создан $age_hours часов назад (максимум: $MAX_AGE_HOURS)" | \
        mail -s "ПРЕДУПРЕЖДЕНИЕ: Устаревший бэкап Alekhin Clinic" "$ALERT_EMAIL"
else
    echo "✅ Бэкапы актуальны"
fi

# Проверка места на диске
disk_usage=$(df "$BACKUP_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 90 ]; then
    echo "⚠️  ПРЕДУПРЕЖДЕНИЕ: Диск заполнен на $disk_usage%"
    echo "Директория бэкапов заполнена на $disk_usage%" | \
        mail -s "ПРЕДУПРЕЖДЕНИЕ: Мало места для бэкапов" "$ALERT_EMAIL"
fi

echo "Всего бэкапов: $(find "$BACKUP_DIR" -name "*.sql.gz" -type f | wc -l)"
echo "Общий размер: $(du -sh "$BACKUP_DIR" | cut -f1)"
EOF

chmod +x "$MONITOR_SCRIPT"

echo ""
echo "📊 Скрипт мониторинга создан:"
echo "cp $MONITOR_SCRIPT /opt/alekhin-clinic/scripts/"
echo "Добавьте в cron для ежечасной проверки:"
echo "0 * * * * /opt/alekhin-clinic/scripts/backup_monitor.sh"

echo ""
echo "🎉 Настройка автоматических бэкапов завершена!"
echo "==============================================="
echo "Выберите один из вариантов:"
echo "1. Cron (рекомендуется для простоты)"
echo "2. Systemd timer (рекомендуется для systemd систем)"
echo "3. Docker Compose (для контейнеризированной среды)"