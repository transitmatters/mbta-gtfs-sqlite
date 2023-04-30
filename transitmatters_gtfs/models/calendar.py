from enum import Enum
from datetime import date
from typing import Literal

from sqlalchemy.types import Date, String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ..utils.enum import gtfs_enum_type


class ServiceDayAvailability(Enum):
    NOT_AVAILABLE = "0"
    AVAILABLE = "1"


TServiceDayAvailability = Literal[
    ServiceDayAvailability.AVAILABLE,
    ServiceDayAvailability.NOT_AVAILABLE,
]


class CalendarService(Base):
    service_id: Mapped[str] = mapped_column(String)
    monday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    tuesday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    wednesday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    thursday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    friday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    saturday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    sunday: Mapped[TServiceDayAvailability] = mapped_column(
        gtfs_enum_type(ServiceDayAvailability)
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
