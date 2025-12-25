# app.py
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, request, jsonify, render_template

from database import SessionLocal, engine, Base
from models import User, Subscription, AuditLog

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("subscriptions.html")


def init_db():
    """Создание таблиц и тестового пользователя."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=1).first()
        if not user:
            user = User(id=1, name="Test User")
            db.add(user)
            db.commit()
    finally:
        db.close()


init_db()


def log_action(db, user_id: int, action: str, subscription_id: int | None):
    """Запись действия в таблицу аудита."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        subscription_id=subscription_id
    )
    db.add(log)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/subscriptions", methods=["POST"])
def create_subscription():
    """
    Создание подписки:
    {
      "name": "Netflix",
      "amount": 499.0,
      "period": "monthly",
      "start_date": "2025-01-01",
      "next_charge_date": "2025-02-01"   # опционально
    }
    """
    data = request.json or {}

    name = data.get("name")
    amount_raw = data.get("amount")
    period = data.get("period")
    start_date_raw = data.get("start_date")
    next_charge_raw = data.get("next_charge_date")

    if not all([name, amount_raw, period, start_date_raw]):
        return jsonify({"error": "name, amount, period, start_date обязательны"}), 400

    try:
        amount = Decimal(str(amount_raw))
    except (InvalidOperation, TypeError):
        return jsonify({"error": "amount должен быть числом"}), 400

    try:
        start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").date()  # Исправлено: добавляем .date()
    except ValueError:
        return jsonify({"error": "start_date в формате YYYY-MM-DD"}), 400

    next_charge_date = None
    if next_charge_raw:
        try:
            next_charge_date = datetime.strptime(next_charge_raw, "%Y-%m-%d").date()  # Исправлено: добавляем .date()
        except ValueError:
            return jsonify({"error": "next_charge_date в формате YYYY-MM-DD"}), 400

    db = SessionLocal()
    try:
        user_id = 1  # один тестовый пользователь
        sub = Subscription(
            user_id=user_id,
            name=name,
            amount=amount,
            period=period,
            start_date=start_date,
            next_charge_date=next_charge_date,
            active=True
        )
        db.add(sub)
        db.flush()  # получаем sub.id до коммита

        log_action(db, user_id=user_id, action="create", subscription_id=sub.id)

        db.commit()
        db.refresh(sub)
        return jsonify(sub.to_dict()), 201
    finally:
        db.close()


@app.route("/subscriptions", methods=["GET"])
def list_subscriptions():
    """Просмотр всех активных подписок пользователя."""
    db = SessionLocal()
    try:
        user_id = 1
        subs = (
            db.query(Subscription)
            .filter_by(user_id=user_id, active=True)
            .all()
        )
        return jsonify([s.to_dict() for s in subs])
    finally:
        db.close()


@app.route("/subscriptions/<int:sub_id>", methods=["PUT"])
def update_subscription(sub_id: int):
    """
    Редактирование подписки:
    можно обновить amount, period, next_charge_date.
    """
    data = request.json or {}
    db = SessionLocal()
    try:
        user_id = 1
        sub = (
            db.query(Subscription)
            .filter_by(id=sub_id, user_id=user_id, active=True)
            .first()
        )
        if not sub:
            return jsonify({"error": "Подписка не найдена"}), 404

        if "amount" in data:
            try:
                sub.amount = Decimal(str(data["amount"]))
            except (InvalidOperation, TypeError):
                return jsonify({"error": "amount должен быть числом"}), 400

        if "period" in data:
            sub.period = data["period"]

        if "next_charge_date" in data:
            raw = data["next_charge_date"]
            if raw is None:
                sub.next_charge_date = None
            else:
                try:
                    sub.next_charge_date = datetime.strptime(raw, "%Y-%m-%d").date()  # Исправлено: добавляем .date()
                except ValueError:
                    return jsonify({"error": "next_charge_date в формате YYYY-MM-DD"}), 400

        log_action(db, user_id=user_id, action="update", subscription_id=sub.id)

        db.commit()
        db.refresh(sub)
        return jsonify(sub.to_dict())
    finally:
        db.close()


@app.route("/subscriptions/<int:sub_id>", methods=["DELETE"])
def delete_subscription(sub_id: int):
    db = SessionLocal()
    try:
        user_id = 1
        sub = (
            db.query(Subscription)
            .filter_by(id=sub_id, user_id=user_id, active=True)
            .first()
        )
        if not sub:
            return jsonify({"error": "Подписка не найдена"}), 404

        sub.active = False
        log_action(db, user_id=user_id, action="delete", subscription_id=sub.id)

        db.commit()
        return jsonify({"status": "deleted"})
    finally:
        db.close()


if __name__ == "__main__":
    app.run(port=5000, debug=True)
