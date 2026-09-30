from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class Problem(db.Model):
    __tablename__ = "problem"

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    resident_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(db.ForeignKey("category.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(30), nullable=False, default="MEDIUM", index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="NEW", index=True)
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    resident: Mapped["User"] = relationship(back_populates="reported_problems")
    category: Mapped["Category"] = relationship(back_populates="problems")
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    status_history: Mapped[list["StatusHistory"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    images: Mapped[list["ProblemImage"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
