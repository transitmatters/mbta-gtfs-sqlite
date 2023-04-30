from enum import Enum
from typing import Literal
import datetime

from sqlalchemy.types import Date, String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ..utils.enum import gtfs_enum_type


class CalendarServiceExceptionType(Enum):
    ADDED = "1"
    REMOVED = "2"


TCalendarServiceExceptionType = Literal[
    CalendarServiceExceptionType.ADDED,
    CalendarServiceExceptionType.REMOVED,
]


class CalendarServiceException(Base):
    service_id: Mapped[str] = mapped_column(String, index=True)
    date: Mapped[datetime.date] = mapped_column(Date)
    exception_type: Mapped[TCalendarServiceExceptionType] = mapped_column(
        gtfs_enum_type(CalendarServiceExceptionType)
    )
    holiday_name: Mapped[str] = mapped_column(String, nullable=True)
