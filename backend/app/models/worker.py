from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Worker(db.Model):
    __tablename__ = "worker"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), unique=True, nullable=False, index=True)
    worker_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    availability_status: Mapped[str] = mapped_column(String(30), nullable=False, default="AVAILABLE", index=True)
    maximum_capacity: Mapped[int] = mapped_column(default=1, nullable=False)
    current_active_jobs: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="worker")
    skills: Mapped[list["WorkerSkill"]] = relationship(back_populates="worker", cascade="all, delete-orphan")
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="worker", cascade="all, delete-orphan")
