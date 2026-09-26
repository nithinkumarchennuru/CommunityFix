from datetime import datetime, timezone

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="resident", index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    worker: Mapped["Worker"] = relationship(back_populates="user", uselist=False)
    reported_problems: Mapped[list["Problem"]] = relationship(
        back_populates="resident",
        foreign_keys="Problem.resident_id",
    )
    changed_status_history: Mapped[list["StatusHistory"]] = relationship(
        back_populates="changed_by_user",
        foreign_keys="StatusHistory.changed_by",
    )
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    uploaded_images: Mapped[list["ProblemImage"]] = relationship(back_populates="uploaded_by_user", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("phone", name="uq_user_phone"),
    )
