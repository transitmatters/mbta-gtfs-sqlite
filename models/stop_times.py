from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base


class StopTime(Base):
    trip_id: Mapped[str] = mapped_column(String)
    stop_id: Mapped[str] = mapped_column(String)
    arrival_time: Mapped[int] = mapped_column(Integer)
    departure_time: Mapped[int] = mapped_column(Integer)
    stop_sequence: Mapped[int] = mapped_column(Integer)
    pickup_type: Mapped[str] = mapped_column(String)
    drop_off_type: Mapped[str] = mapped_column(String)
    continuous_pickup: Mapped[str] = mapped_column(String)
    continuous_drop_off: Mapped[str] = mapped_column(String)
