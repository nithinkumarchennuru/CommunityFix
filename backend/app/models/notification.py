from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Notification(db.Model):
    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False, index=True)
    problem_id: Mapped[int] = mapped_column(db.ForeignKey("problem.id"), nullable=True, index=True)
    assignment_id: Mapped[int] = mapped_column(db.ForeignKey("assignment.id"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False, index=True)
    read_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)

    user: Mapped["User"] = relationship(back_populates="notifications")
    problem: Mapped["Problem"] = relationship(back_populates="notifications")
    assignment: Mapped["Assignment"] = relationship(back_populates="notifications")

    __table_args__ = (
        Index("ix_notification_user_unread", "user_id", "is_read"),
    )
