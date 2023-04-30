from datetime import date

from sqlalchemy.types import Date, String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class FeedInfo(Base):
    feed_publisher_name: Mapped[str] = mapped_column(String)
    feed_publisher_url: Mapped[str] = mapped_column(String)
    feed_lang: Mapped[str] = mapped_column(String)
    feed_start_date: Mapped[date] = mapped_column(Date)
    feed_end_date: Mapped[date] = mapped_column(Date)
    feed_version: Mapped[str] = mapped_column(String)
    feed_contact_email: Mapped[str] = mapped_column(String, nullable=True)
    feed_contact_url: Mapped[str] = mapped_column(String, nullable=True)
    # These are not part of GTFS
    retrieved_from_url: Mapped[str] = mapped_column(String)
    zip_md5_checksum: Mapped[str] = mapped_column(String)
