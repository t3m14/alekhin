#!/bin/bash
# backup_monitor.sh
# Мониторинг состояния бэкапов Alekhin Clinic

set -e

# ===========================================
# КОНФИГУРАЦИЯ
# ===========================================

BACKUP_DIR="/backups"
ALERT_EMAIL="admin@alekhin-clinic.com"
MAX_AGE_HOURS=26  # Максимальный возраст последнего бэкапа (26 часов = учитываем возможную задержку)
MIN_BACKUP_SIZE=1048576  # Минимальный размер бэкапа в байтах (1MB)
DISK_USAGE_THRESHOLD=90  # Предупреждение при заполнении диска свыше 90%
MIN_FREE_SPACE_GB=5  # Минимум свободного места в GB

# Telegram настройки (опционально)
TELEGRAM_BOT_TOKEN=""  # Вставьте токен вашего бота
TELEGRAM_CHAT_ID=""    # Вставьте ID чата

# ===========================================
# ЦВЕТА ДЛЯ ВЫВОДА
# ===========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ===========================================
# ФУНКЦИИ ЛОГИРОВАНИЯ
# ===========================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# ===========================================
# ФУНКЦИИ УВЕДОМЛЕНИЙ
# ===========================================

send_telegram_alert() {
    local message="$1"
    local priority="$2"  # INFO, WARNING, ERROR, CRITICAL
    
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        local emoji=""
        case "$priority" in
            "INFO") emoji="ℹ️" ;;
            "WARNING") emoji="⚠️" ;;
            "ERROR") emoji="❌" ;;
            "CRITICAL") emoji="🚨" ;;
            *) emoji="📊" ;;
        esac
        
        local formatted_message="${emoji} *${priority}* - Alekhin Clinic Backup Monitor

${message}

📅 $(date '+%Y-%m-%d %H:%M:%S')"
        
        curl -s -X POST \
            "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$formatted_message" \
            -d "parse_mode=Markdown" > /dev/null 2>&1
    fi
}

send_email_alert() {
    local subject="$1"
    local message="$2"
    
    if [ -n "$ALERT_EMAIL" ] && command -v mail >/dev/null 2>&1; then
        echo "$message" | mail -s "[$HOSTNAME] $subject" "$ALERT_EMAIL" 2>/dev/null || true
    fi
}

# ===========================================
# ФУНКЦИИ ПРОВЕРОК
# ===========================================

check_backup_directory() {
    log_info "Проверка директории бэкапов..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_critical "Директория бэкапов не существует: $BACKUP_DIR"
        send_telegram_alert "Директория бэкапов не найдена: $BACKUP_DIR" "CRITICAL"
        send_email_alert "КРИТИЧНО: Директория бэкапов не найдена" "Директория $BACKUP_DIR не существует на сервере $HOSTNAME"
        return 1
    fi
    
    if [ ! -w "$BACKUP_DIR" ]; then
        log_error "Нет прав записи в директорию бэкапов: $BACKUP_DIR"
        send_telegram_alert "Нет прав записи в директорию бэкапов" "ERROR"
        return 1
    fi
    
    log_success "Директория бэкапов доступна"
    return 0
}

check_latest_backup() {
    log_info "Проверка актуальности последнего бэкапа..."
    
    # Находим последний бэкап базы данных
    local latest_backup=$(find "$BACKUP_DIR" -name "*backup_*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1)
    
    if [ -z "$latest_backup" ]; then
        log_critical "Бэкапы базы данных не найдены!"
        send_telegram_alert "Бэкапы базы данных отсутствуют в директории $BACKUP_DIR" "CRITICAL"
        send_email_alert "КРИТИЧНО: Бэкапы БД не найдены" "В директории $BACKUP_DIR не найдено ни одного файла бэкапа базы данных"
        return 1
    fi
    
    local backup_timestamp=$(echo "$latest_backup" | cut -d' ' -f1)
    local backup_file=$(echo "$latest_backup" | cut -d' ' -f2-)
    local backup_name=$(basename "$backup_file")
    
    local current_time=$(date +%s)
    local backup_age_seconds=$((current_time - ${backup_timestamp%.*}))
    local backup_age_hours=$((backup_age_seconds / 3600))
    local backup_age_minutes=$(((backup_age_seconds % 3600) / 60))
    
    # Проверяем размер файла
    local backup_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null || echo "0")
    local backup_size_hr=$(du -h "$backup_file" 2>/dev/null | cut -f1 || echo "0B")
    
    log_info "Последний бэкап: $backup_name"
    log_info "Возраст: ${backup_age_hours}ч ${backup_age_minutes}м"
    log_info "Размер: $backup_size_hr"
    
    # Проверяем возраст
    if [ "$backup_age_hours" -gt "$MAX_AGE_HOURS" ]; then
        log_error "Бэкап устарел! Возраст: ${backup_age_hours}ч (максимум: ${MAX_AGE_HOURS}ч)"
        send_telegram_alert "Устаревший бэкап!
        
Файл: $backup_name
Возраст: ${backup_age_hours}ч ${backup_age_minutes}м
Максимум: ${MAX_AGE_HOURS}ч" "ERROR"
        send_email_alert "ОШИБКА: Устаревший бэкап" "Последний бэкап был создан $backup_age_hours часов назад. Максимально допустимый возраст: $MAX_AGE_HOURS часов."
        return 1
    fi
    
    # Проверяем размер
    if [ "$backup_size" -lt "$MIN_BACKUP_SIZE" ]; then
        log_error "Бэкап слишком мал! Размер: $backup_size_hr (минимум: $((MIN_BACKUP_SIZE / 1024 / 1024))MB)"
        send_telegram_alert "Подозрительно маленький бэкап!
        
Файл: $backup_name
Размер: $backup_size_hr
Возможна ошибка создания бэкапа" "ERROR"
        return 1
    fi
    
    # Проверяем целостность
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log_error "Бэкап поврежден! Файл: $backup_name"
        send_telegram_alert "Поврежденный бэкап!
        
Файл: $backup_name
Ошибка: файл не является валидным gzip архивом" "CRITICAL"
        return 1
    fi
    
    log_success "Последний бэкап актуален и валиден"
    return 0
}

check_disk_space() {
    log_info "Проверка места на диске..."
    
    # Получаем информацию о диске
    local disk_info=$(df "$BACKUP_DIR" | tail -1)
    local disk_usage_percent=$(echo "$disk_info" | awk '{print $5}' | sed 's/%//')
    local available_space_kb=$(echo "$disk_info" | awk '{print $4}')
    local available_space_gb=$((available_space_kb / 1024 / 1024))
    
    log_info "Использование диска: ${disk_usage_percent}%"
    log_info "Свободно: ${available_space_gb}GB"
    
    # Проверяем процент использования
    if [ "$disk_usage_percent" -gt "$DISK_USAGE_THRESHOLD" ]; then
        log_warning "Диск заполнен на ${disk_usage_percent}% (порог: ${DISK_USAGE_THRESHOLD}%)"
        send_telegram_alert "Мало места на диске!
        
Использование: ${disk_usage_percent}%
Свободно: ${available_space_gb}GB
Директория: $BACKUP_DIR" "WARNING"
        send_email_alert "ПРЕДУПРЕЖДЕНИЕ: Мало места на диске" "Диск с бэкапами заполнен на $disk_usage_percent%. Свободно: ${available_space_gb}GB"
    fi
    
    # Проверяем абсолютное количество свободного места
    if [ "$available_space_gb" -lt "$MIN_FREE_SPACE_GB" ]; then
        log_error "Критически мало свободного места: ${available_space_gb}GB (минимум: ${MIN_FREE_SPACE_GB}GB)"
        send_telegram_alert "Критически мало места!
        
Свободно: ${available_space_gb}GB
Минимум: ${MIN_FREE_SPACE_GB}GB
Необходима очистка старых бэкапов!" "ERROR"
        return 1
    fi
    
    log_success "Достаточно места на диске"
    return 0
}

check_backup_consistency() {
    log_info "Проверка консистентности бэкапов..."
    
    # Проверяем, есть ли бэкапы за последние 7 дней
    local recent_backups=$(find "$BACKUP_DIR" -name "*backup_*.sql.gz" -type f -mtime -7 | wc -l)
    
    if [ "$recent_backups" -eq 0 ]; then
        log_error "Нет бэкапов за последние 7 дней!"
        send_telegram_alert "Отсутствуют свежие бэкапы!
        
Не найдено ни одного бэкапа за последние 7 дней" "ERROR"
        return 1
    fi
    
    log_info "Найдено $recent_backups бэкапов за последние 7 дней"
    
    # Проверяем регулярность создания бэкапов
    local yesterday=$(date -d "yesterday" +%Y%m%d)
    local yesterday_backup=$(find "$BACKUP_DIR" -name "*backup_${yesterday}_*.sql.gz" -type f)
    
    if [ -z "$yesterday_backup" ]; then
        log_warning "Не найден вчерашний бэкап (возможно, это нормально в выходные)"
    else
        log_success "Вчерашний бэкап найден: $(basename "$yesterday_backup")"
    fi
    
    return 0
}

check_docker_containers() {
    log_info "Проверка состояния Docker контейнеров..."
    
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "Docker не установлен или недоступен"
        return 1
    fi
    
    # Проверяем основные контейнеры
    local containers=("backend" "db")
    local all_running=true
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "^${container}$"; then
            log_success "Контейнер $container запущен"
        else
            log_warning "Контейнер $container не запущен"
            all_running=false
        fi
    done
    
    if [ "$all_running" = false ]; then
        send_telegram_alert "Некоторые контейнеры не запущены!
        
Проверьте состояние сервисов Docker" "WARNING"
    fi
    
    return 0
}

generate_report() {
    local start_time="$1"
    local end_time="$2"
    local checks_passed="$3"
    local total_checks="$4"
    
    local duration=$((end_time - start_time))
    local status="✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ"
    local status_emoji="✅"
    
    if [ "$checks_passed" -ne "$total_checks" ]; then
        status="⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ"
        status_emoji="⚠️"
    fi
    
    # Статистика бэкапов
    local total_backups=$(find "$BACKUP_DIR" -name "*.sql.gz" -type f 2>/dev/null | wc -l)
    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "N/A")
    local latest_backup=$(find "$BACKUP_DIR" -name "*backup_*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
    local latest_backup_name=$(basename "$latest_backup" 2>/dev/null || echo "N/A")
    
    # Информация о системе
    local hostname=$(hostname)
    local uptime=$(uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')
    local load_avg=$(uptime | awk -F'load average:' '{print $2}')
    
    local report="${status_emoji} *Отчет мониторинга бэкапов*
🏥 *Alekhin Clinic*

📊 *Статус:* $status
🕐 *Время проверки:* $(date '+%Y-%m-%d %H:%M:%S')
⏱ *Длительность:* ${duration}с
✅ *Пройдено проверок:* ${checks_passed}/${total_checks}

📦 *Статистика бэкапов:*
• Всего бэкапов: $total_backups
• Общий размер: $total_size
• Последний: $latest_backup_name

🖥 *Система:*
• Сервер: $hostname
• Uptime: $uptime
• Load Average:$load_avg

📁 *Директория:* $BACKUP_DIR"

    echo "$report"
    
    # Отправляем уведомления только при проблемах или раз в день
    local current_hour=$(date +%H)
    if [ "$checks_passed" -ne "$total_checks" ] || [ "$current_hour" = "08" ]; then
        if [ "$checks_passed" -ne "$total_checks" ]; then
            send_telegram_alert "$report" "WARNING"
            send_email_alert "Проблемы с бэкапами Alekhin Clinic" "$report"
        else
            send_telegram_alert "$report" "INFO"
        fi
    fi
}

# ===========================================
# ГЛАВНАЯ ФУНКЦИЯ
# ===========================================

main() {
    local start_time=$(date +%s)
    local checks_passed=0
    local total_checks=5
    
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  📊 МОНИТОРИНГ БЭКАПОВ ALEKHIN CLINIC  ${NC}"
    echo -e "${PURPLE}========================================${NC}"
    log_info "Запуск мониторинга на $(hostname)"
    
    # Выполняем проверки
    if check_backup_directory; then
        ((checks_passed++))
    fi
    
    if check_latest_backup; then
        ((checks_passed++))
    fi
    
    if check_disk_space; then
        ((checks_passed++))
    fi
    
    if check_backup_consistency; then
        ((checks_passed++))
    fi
    
    if check_docker_containers; then
        ((checks_passed++))
    fi
    
    local end_time=$(date +%s)
    
    echo ""
    echo -e "${PURPLE}========================================${NC}"
    
    # Генерируем отчет
    generate_report "$start_time" "$end_time" "$checks_passed" "$total_checks"
    
    if [ "$checks_passed" -eq "$total_checks" ]; then
        log_success "🎉 Все проверки пройдены успешно!"
        exit 0
    else
        log_error "❌ Обнаружено проблем: $((total_checks - checks_passed))"
        exit 1
    fi
}

# ===========================================
# ОБРАБОТКА АРГУМЕНТОВ
# ===========================================

case "${1:-}" in
    --quiet)
        # Тихий режим - только ошибки
        main 2>/dev/null | grep -E "(ERROR|CRITICAL|WARNING)" || true
        ;;
    --json)
        # JSON вывод для интеграции с мониторингом
        echo '{"timestamp":"'$(date -Iseconds)'","status":"checking","checks":[]}'
        main > /dev/null 2>&1
        echo '{"timestamp":"'$(date -Iseconds)'","status":"completed","exit_code":'$?'}'
        ;;
    --help)
        echo "Мониторинг бэкапов Alekhin Clinic"
        echo ""
        echo "Использование: $0 [опция]"
        echo ""
        echo "Опции:"
        echo "  (без опций)  Полная проверка с выводом"
        echo "  --quiet      Тихий режим (только ошибки)"
        echo "  --json       JSON вывод для автоматизации"
        echo "  --help       Показать эту справку"
        echo ""
        echo "Коды возврата:"
        echo "  0  Все проверки пройдены"
        echo "  1  Обнаружены проблемы"
        ;;
    *)
        main
        ;;
esac