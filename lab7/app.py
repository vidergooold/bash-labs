from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os

app = Flask(__name__)

# Раздел II.3.a — общее ограничение: 100 запросов в сутки
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"]
)

# Раздел II.1 — Хранилище передаётся словарём data
DATA_FILE = "data.json"
data = {}


# Раздел II.1.a — загрузка данных при старте приложения
def load_data():
    global data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        data = {}


# Раздел II.1.b — сохранение данных после каждой операции
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


load_data()


# Раздел II.2 — Создание API с Flask-Limiter

# Раздел II.3.b — лимит 10 запросов/мин для операций /set
# Раздел II.2.a — POST /set — сохранить ключ-значение
@limiter.limit("10 per minute")
@app.route("/set", methods=["POST"])
def set_value():
    body = request.json
    key = body.get("key")
    value = body.get("value")

    if key is None or value is None:
        return jsonify({"error": "Передайте key и value"}), 400

    data[key] = value
    save_data()
    return jsonify({"message": "Сохранено", "saved": {key: value}})


# Раздел II.2.b — GET /get/<key> — получить значение по ключу
@app.route("/get/<key>", methods=["GET"])
def get_value(key):
    if key not in data:
        return jsonify({"error": "Ключ не найден"}), 404
    return jsonify({"key": key, "value": data[key]})


# Раздел II.3.b — лимит 10 запросов/мин для /delete
# Раздел II.2.c — DELETE /delete/<key> — удалить ключ
@limiter.limit("10 per minute")
@app.route("/delete/<key>", methods=["DELETE"])
def delete_value(key):
    if key not in data:
        return jsonify({"error": "Ключ не существует"}), 404

    del data[key]
    save_data()
    return jsonify({"message": f"Ключ '{key}' удалён"})


# Раздел II.2.d — GET /exists/<key> — проверка наличия ключа
@app.route("/exists/<key>", methods=["GET"])
def exists_value(key):
    return jsonify({"key": key, "exists": key in data})


# Раздел II — запуск приложения
if __name__ == "__main__":
    print("Key-Value хранилище запущено на порту 5000")
    app.run(port=5000)
