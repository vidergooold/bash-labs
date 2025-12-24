# models.py
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, String, Numeric, Date, Boolean,
    ForeignKey, DateTime
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    subscriptions = relationship("Subscription", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    period = Column(String, nullable=False)  # ежемесячно, ежегодно и т.д.
    start_date = Column(Date, nullable=False)
    next_charge_date = Column(Date, nullable=True)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions")
    audit_logs = relationship("AuditLog", back_populates="subscription")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "amount": float(self.amount) if self.amount is not None else None,
            "period": self.period,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "next_charge_date": (
                self.next_charge_date.isoformat()
                if self.next_charge_date else None
            ),
            "active": self.active,
        }


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    action = Column(String, nullable=False)  # create / update / delete
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="audit_logs")
    subscription = relationship("Subscription", back_populates="audit_logs")
