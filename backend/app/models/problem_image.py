from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class ProblemImage(db.Model):
    __tablename__ = "problem_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(db.ForeignKey("problem.id"), nullable=False, index=True)
    uploaded_by: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_id: Mapped[str] = mapped_column(String(255), nullable=False)
    image_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True, default="PROBLEM")
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False, index=True)

    problem: Mapped["Problem"] = relationship(back_populates="images")
    uploaded_by_user: Mapped["User"] = relationship(back_populates="uploaded_images")

    __table_args__ = (
        Index("ix_problem_image_problem_type", "problem_id", "image_type"),
        Index("ix_problem_image_user_type", "uploaded_by", "image_type"),
    )
