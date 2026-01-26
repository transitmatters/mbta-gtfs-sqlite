from sqlalchemy.types import String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Agency(Base):
    agency_id: Mapped[str] = mapped_column(String)
    agency_name: Mapped[str] = mapped_column(String)
    agency_url: Mapped[str] = mapped_column(String)
    agency_timezone: Mapped[str] = mapped_column(String)
    agency_lang: Mapped[str] = mapped_column(String, nullable=True)
    agency_phone: Mapped[str] = mapped_column(String, nullable=True)
    agency_fare_url: Mapped[str] = mapped_column(String, nullable=True)
    agency_email: Mapped[str] = mapped_column(String, nullable=True)
