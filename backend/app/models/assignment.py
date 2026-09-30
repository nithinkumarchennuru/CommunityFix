from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Assignment(db.Model):
    __tablename__ = "assignment"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(db.ForeignKey("problem.id"), nullable=False, index=True)
    worker_id: Mapped[int | None] = mapped_column(db.ForeignKey("worker.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="ASSIGNED", index=True)
    assigned_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    reassigned_at: Mapped[datetime | None] = mapped_column(default=None, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    problem: Mapped["Problem"] = relationship(back_populates="assignments")
    worker: Mapped["Worker"] = relationship(back_populates="assignments")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="assignment", cascade="all, delete-orphan")
