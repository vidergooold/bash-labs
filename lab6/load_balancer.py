from flask import Flask, request, jsonify, render_template_string, redirect
import requests
import threading
import time

app = Flask(__name__)

# --- Пул инстансов ---
instances = [
    {"ip": "127.0.0.1", "port": 5001, "active": True},
    {"ip": "127.0.0.1", "port": 5002, "active": True},
    {"ip": "127.0.0.1", "port": 5003, "active": True},
]

current_index = 0  # Round Robin указатель


# ФУНКЦИЯ ПРОВЕРКИ ДОСТУПНОСТИ ИНСТАНСОВ
def health_check_loop():
    while True:
        for inst in instances:
            try:
                url = f"http://{inst['ip']}:{inst['port']}/health"
                response = requests.get(url, timeout=1)
                inst["active"] = (response.status_code == 200)
            except:
                inst["active"] = False

        time.sleep(5)


# Запускаем проверку в отдельном потоке
threading.Thread(target=health_check_loop, daemon=True).start()


# ROUND ROBIN ВЫБОР ИНСТАНСА
def get_next_instance():
    global current_index

    active_instances = [i for i in instances if i["active"]]

    if not active_instances:
        return None

    inst = active_instances[current_index % len(active_instances)]
    current_index += 1
    return inst


# ЭНДПОИНТЫ БАЛАНСИРОВЩИКА

@app.route("/health")
def balancer_health():
    return jsonify(instances)


@app.route("/process")
def process_request():
    inst = get_next_instance()

    if not inst:
        return jsonify({"error": "Нет активных инстансов"}), 503

    url = f"http://{inst['ip']}:{inst['port']}/process"
    resp = requests.get(url)
    return resp.json()


# WEB UI

HTML_TEMPLATE = """
<h1>Load Balancer UI</h1>

<h3>Активные инстансы:</h3>

<table border="1" cellpadding="5">
<tr><th>#</th><th>IP</th><th>Port</th><th>Status</th><th>Action</th></tr>

{% for inst in instances %}
<tr>
    <td>{{ loop.index0 }}</td>
    <td>{{ inst.ip }}</td>
    <td>{{ inst.port }}</td>
    <td>{{ "ACTIVE" if inst.active else "DOWN" }}</td>
    <td>
        <form action="/remove_instance" method="post">
            <input type="hidden" name="index" value="{{ loop.index0 }}">
            <button type="submit">Удалить</button>
        </form>
    </td>
</tr>
{% endfor %}
</table>

<h3>Добавить новый инстанс:</h3>

<form action="/add_instance" method="post">
    IP: <input type="text" name="ip" required>
    Port: <input type="number" name="port" required>
    <button type="submit">Добавить</button>
</form>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, instances=instances)


@app.route("/add_instance", methods=["POST"])
def add_instance():
    ip = request.form["ip"]
    port = int(request.form["port"])

    instances.append({"ip": ip, "port": port, "active": True})
    return redirect("/")


@app.route("/remove_instance", methods=["POST"])
def remove_instance():
    index = int(request.form["index"])
    if 0 <= index < len(instances):
        instances.pop(index)
    return redirect("/")


# ПЕРЕХВАТ ВСЕХ ПРОЧИХ ЗАПРОСОВ

@app.route("/<path:path>")
def catch_all(path):
    inst = get_next_instance()

    if not inst:
        return jsonify({"error": "Нет активных инстансов"}), 503

    url = f"http://{inst['ip']}:{inst['port']}/{path}"

    try:
        resp = requests.get(url)
        return resp.text
    except:
        return jsonify({"error": "Инстанс недоступен"}), 503


# ЗАПУСК СЕРВЕРА

if __name__ == "__main__":
    print("Балансировщик работает на порту 8000")
    app.run(port=8000)
