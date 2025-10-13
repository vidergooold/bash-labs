#!/bin/bash

# Автоматический мигратор SQL-скриптов для PostgreSQL
# Лабораторная работа №2

# Загружаем переменные из .env файла
if [ -f .env ]; then
    source .env
else
    echo " Файл .env не найден"
    exit 1
fi

# Параметры подключения к базе данных
DB_NAME="migration_db"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
MIGRATIONS_DIR="./migrations"
export PGPASSWORD="$DB_PASSWORD"

# Функция для выполнения SQL из файла
run_sql() {
    local file="$1"
    psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$file" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo " Файл $file успешно выполнен"
        return 0
    else
        echo " Ошибка при выполнении файла $file"
        return 1
    fi
}

# Функция для выполнения SQL команды
run_sql_c() {
    local sql="$1"
    psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -t -c "$sql" 2>/dev/null
}

# Функция для проверки подключения к БД
check_db_connection() {
    echo " Проверка подключения к базе данных..."
    if run_sql_c "SELECT 1;" > /dev/null 2>&1; then
        echo " Подключение к БД успешно"
        return 0
    else
        echo " Не удалось подключиться к БД"
        echo "Проверьте параметры подключения:"
        echo "  База данных: $DB_NAME"
        echo "  Пользователь: $DB_USER"
        echo "  Хост: $DB_HOST"
        echo "  Порт: $DB_PORT"
        return 1
    fi
}

# Функция для создания таблицы миграций
create_migrations_table() {
    echo " Создание таблицы migrations..."
    
    local create_table_sql="CREATE TABLE IF NOT EXISTS migrations (
        id SERIAL PRIMARY KEY,
        migration_name VARCHAR(255) UNIQUE NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"
    
    run_sql_c "$create_table_sql" > /dev/null
    echo " Таблица migrations готова к работе"
}

# Надежная функция проверки Applied ли миграция
is_migration_applied() {
    local migration_name="$1"
    local result
    result=$(run_sql_c "SELECT COUNT(*) FROM migrations WHERE migration_name = '$migration_name';")
    result=$(echo "$result" | tr -d '[:space:]')
    [ "$result" -eq "1" ]
}

# Функция для получения списка примененных миграций
get_applied_migrations() {
    run_sql_c "SELECT migration_name FROM migrations ORDER BY applied_at;" | sed '/^$/d'
}

# Функция для применения миграций
apply_migrations() {
    echo " Начало применения миграций..."
    echo
    
    # Проверяем существование директории с миграциями
    if [ ! -d "$MIGRATIONS_DIR" ]; then
        echo " Директория миграций $MIGRATIONS_DIR не существует"
        return 1
    fi
    
    # Счетчики для статистики
    local applied_count=0
    local skipped_count=0
    
    # Перебираем все SQL файлы в директории
    for sql_file in "$MIGRATIONS_DIR"/*.sql; do
        # Проверяем, существует ли файл
        if [ ! -f "$sql_file" ]; then
            continue
        fi
        
        # Получаем имя файла без пути
        local migration_name
        migration_name=$(basename "$sql_file")
        
        # Проверяем, была ли миграция уже применена
        if is_migration_applied "$migration_name"; then
            echo "  $migration_name - уже применена"
            ((skipped_count++))
        else
            echo " $migration_name - применение..."
            
            # Выполняем SQL скрипт
            if run_sql "$sql_file"; then
                # Записываем информацию о примененной миграции
                local insert_sql="INSERT INTO migrations (migration_name) VALUES ('$migration_name');"
                if run_sql_c "$insert_sql" > /dev/null; then
                    echo " $migration_name - успешно применена"
                    ((applied_count++))
                else
                    echo " $migration_name - ошибка записи в таблицу migrations"
                fi
            else
                echo " $migration_name - ошибка выполнения SQL"
            fi
        fi
        echo
    done
    
    echo "=========================================="
    echo "СТАТИСТИКА ПРИМЕНЕНИЯ МИГРАЦИЙ:"
    echo " Применено новых: $applied_count"
    echo " Пропущено: $skipped_count"
    echo "=========================================="
}

# Функция для отображения статуса миграций
show_migration_status() {
    echo "Текущий статус миграций:"
    echo "=========================================="
    
    local applied_migrations
    applied_migrations=$(get_applied_migrations)
    
    if [ -z "$applied_migrations" ]; then
        echo "Нет примененных миграций"
    else
        echo "Примененные миграции:"
        echo "$applied_migrations"
    fi
    
    echo "------------------------------------------"
    
    # Показываем доступные миграции
    if [ -d "$MIGRATIONS_DIR" ]; then
        local available_migrations
        available_migrations=$(find "$MIGRATIONS_DIR" -name "*.sql" -exec basename {} \; | sort)
        
        if [ -z "$available_migrations" ]; then
            echo "Доступные миграции: нет файлов .sql"
        else
            echo "Доступные миграции:"
            echo "$available_migrations"
        fi
    else
        echo " Директория миграций не существует"
    fi
    echo
}

# Основная функция
main() {
    echo "=========================================="
    echo "   АВТОМАТИЧЕСКИЙ МИГРАТОР POSTGRESQL"
    echo "   Лабораторная работа №2"
    echo "=========================================="
    echo
    
    # Проверяем подключение к БД
    if ! check_db_connection; then
        exit 1
    fi
    echo
    
    # Создаем таблицу миграций
    create_migrations_table
    echo
    
    # Показываем текущий статус
    show_migration_status
    
    # Применяем миграции
    apply_migrations
    
    echo
    echo "Работа мигратора завершена"
}

# Запуск основной функции
main "$@"