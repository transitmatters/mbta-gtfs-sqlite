from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base


class TripSummary(Base):
    trip_id: Mapped[str] = mapped_column(String)
    start_time: Mapped[int] = mapped_column(Integer)
    end_time: Mapped[int] = mapped_column(Integer)
