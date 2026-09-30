from datetime import datetime, timezone

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class StatusHistory(db.Model):
    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(db.ForeignKey("problem.id"), nullable=False, index=True)
    old_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    new_status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    changed_by: Mapped[int | None] = mapped_column(db.ForeignKey("user.id"), nullable=True, index=True)
    changed_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    problem: Mapped["Problem"] = relationship(back_populates="status_history")
    changed_by_user: Mapped["User"] = relationship(back_populates="changed_status_history")
