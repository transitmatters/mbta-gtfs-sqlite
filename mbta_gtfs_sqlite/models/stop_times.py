from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class StopTime(Base):
    trip_id: Mapped[str] = mapped_column(String, index=True)
    stop_id: Mapped[str] = mapped_column(String, index=True)
    arrival_time: Mapped[int] = mapped_column(Integer)
    departure_time: Mapped[int] = mapped_column(Integer)
    stop_sequence: Mapped[int] = mapped_column(Integer)
    stop_headsign: Mapped[str] = mapped_column(String)
    pickup_type: Mapped[str] = mapped_column(String)
    drop_off_type: Mapped[str] = mapped_column(String)
    timepoint: Mapped[str] = mapped_column(String)
    checkpoint_id: Mapped[str] = mapped_column(String)
    continuous_pickup: Mapped[str] = mapped_column(String, nullable=True)
    continuous_drop_off: Mapped[str] = mapped_column(String, nullable=True)
