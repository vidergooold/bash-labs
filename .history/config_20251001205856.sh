#!/bin/bash

# Конфигурационный файл для мигратора
# Настройте параметры подключения к вашей БД

export DB_NAME="migration_db"
export DB_USER="postgres"
export DB_HOST="localhost"
export DB_PORT="5432"
export MIGRATIONS_DIR="./migrations"