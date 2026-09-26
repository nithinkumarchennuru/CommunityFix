from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class WorkerSkill(db.Model):
    __tablename__ = "worker_skill"

    id: Mapped[int] = mapped_column(primary_key=True)
    worker_id: Mapped[int] = mapped_column(db.ForeignKey("worker.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(db.ForeignKey("category.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)

    worker: Mapped["Worker"] = relationship(back_populates="skills")
    category: Mapped["Category"] = relationship(back_populates="worker_skills")

    __table_args__ = (
        UniqueConstraint("worker_id", "category_id", name="uq_worker_skill_worker_category"),
    )
