from enum import Enum
from typing import Literal

from sqlalchemy.types import Date, String
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base
from utils.enum import gtfs_enum_type


class CalendarServiceExceptionType(Enum):
    ADDED = "1"
    REMOVED = "2"


TCalendarServiceExceptionType = Literal[
    CalendarServiceExceptionType.ADDED,
    CalendarServiceExceptionType.REMOVED,
]


class CalendarServiceException(Base):
    service_id: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)
    exception_type: Mapped[TCalendarServiceExceptionType] = mapped_column(
        gtfs_enum_type(CalendarServiceExceptionType)
    )
