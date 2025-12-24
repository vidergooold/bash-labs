#!/usr/bin/env bash
set -e

VENV_DIR="venv"

# 1. setup_database: создание таблиц PostgreSQL
setup_database() {
  echo "[*] Создание таблиц в PostgreSQL..."
  python - << 'EOF'
from database import engine, Base
import models  # важно, чтобы модели были импортированы

Base.metadata.create_all(bind=engine)
print("Таблицы созданы.")
EOF
}

# 2. install_dependencies: venv + pip install
install_dependencies() {
  echo "[*] Создание виртуального окружения..."
  python -m venv "$VENV_DIR"

  # активация для bash / git-bash
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate"

  echo "[*] Установка зависимостей..."
  pip install --upgrade pip
  pip install -r requirements.txt
}

# 3. start_app: запуск Flask-приложения
start_app() {
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate"

  echo "[*] Запуск приложения..."
  python app.py &

  APP_PID=$!
  echo "$APP_PID" > app.pid
  echo "Приложение запущено, PID=$APP_PID"
}

# 4. stop_app: остановка Flask-приложения
stop_app() {
  if [ -f app.pid ]; then
    PID=$(cat app.pid)
    echo "[*] Останавливаю процесс $PID..."
    kill "$PID" || echo "Процесс уже остановлен"
    rm app.pid
  else
    echo "Файл app.pid не найден, приложение, возможно, не запущено."
  fi
}

# 5. run_tests: запуск unit-тестов
run_tests() {
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate"

  echo "[*] Запуск тестов..."
  pytest
}

case "$1" in
  setup_database)
    setup_database
    ;;
  install_dependencies)
    install_dependencies
    ;;
  start_app)
    start_app
    ;;
  stop_app)
    stop_app
    ;;
  run_tests)
    run_tests
    ;;
  *)
    echo "Использование: $0 {setup_database|install_dependencies|start_app|stop_app|run_tests}"
    exit 1
    ;;
esac
