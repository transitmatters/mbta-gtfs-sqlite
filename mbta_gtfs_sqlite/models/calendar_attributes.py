from enum import Enum
from typing import Literal
from datetime import date

from sqlalchemy.types import String, Date
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ..utils.enum import gtfs_enum_type


class ServiceScheduleTypicality(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    NOT_DEFINED = "0"
    MINOR_MODIFICATIONS = "1"
    EXTRA_SERVICE = "2"
    REDUCED_TO_WEEKEND_SERVICE = "3"
    MAJOR_PLANNED_DISRUPTION = "4"
    MAJOR_ATYPICAL_REDUCTIONS = "5"


TServiceScheduleTypicality = Literal[
    ServiceScheduleTypicality.NOT_DEFINED,
    ServiceScheduleTypicality.MINOR_MODIFICATIONS,
    ServiceScheduleTypicality.EXTRA_SERVICE,
    ServiceScheduleTypicality.REDUCED_TO_WEEKEND_SERVICE,
    ServiceScheduleTypicality.MAJOR_PLANNED_DISRUPTION,
    ServiceScheduleTypicality.MAJOR_ATYPICAL_REDUCTIONS,
]


class CalendarAttribute(Base):
    service_id: Mapped[str] = mapped_column(String, index=True)
    service_description: Mapped[str] = mapped_column(String)
    service_schedule_name: Mapped[str] = mapped_column(String)
    service_schedule_type: Mapped[str] = mapped_column(String)
    service_schedule_typicality: Mapped[TServiceScheduleTypicality] = mapped_column(
        gtfs_enum_type(ServiceScheduleTypicality)
    )
    rating_start_date: Mapped[date] = mapped_column(Date, nullable=True)
    rating_end_date: Mapped[date] = mapped_column(Date, nullable=True)
    rating_description: Mapped[str] = mapped_column(String, nullable=True)
