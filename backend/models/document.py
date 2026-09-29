from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    upload_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )