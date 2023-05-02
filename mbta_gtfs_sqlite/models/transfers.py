from enum import Enum
from typing import Literal

from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ..utils.enum import gtfs_enum_type


class TransferType(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    RECOMMENDED = "0"
    TIMED = "1"
    REQUIRES_MINIMUM_TIME = "2"
    NOT_POSSIBLE = "3"
    IN_SEAT = "4"
    MUST_REBOARD = "5"


TTranferType = Literal[
    TransferType.RECOMMENDED,
    TransferType.TIMED,
    TransferType.REQUIRES_MINIMUM_TIME,
    TransferType.NOT_POSSIBLE,
    TransferType.IN_SEAT,
    TransferType.MUST_REBOARD,
]


class WheelchairAccessibility(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    NO_INFORMATION = "0"
    ACCESSIBLE = "1"
    NOT_ACCESSIBLE = "2"


TWheelchairAccessibility = Literal[
    WheelchairAccessibility.NO_INFORMATION,
    WheelchairAccessibility.ACCESSIBLE,
    WheelchairAccessibility.NOT_ACCESSIBLE,
]


class Transfer(Base):
    from_stop_id: Mapped[str] = mapped_column(String)
    to_stop_id: Mapped[str] = mapped_column(String)
    transfer_type: Mapped[TTranferType] = mapped_column(gtfs_enum_type(TransferType))
    min_transfer_time: Mapped[int] = mapped_column(Integer, nullable=True)
    min_walk_time: Mapped[int] = mapped_column(Integer, nullable=True)
    min_wheelchair_time: Mapped[int] = mapped_column(Integer, nullable=True)
    suggested_buffer_time: Mapped[int] = mapped_column(Integer, nullable=True)
    wheelchair_transfer: Mapped[TWheelchairAccessibility] = mapped_column(
        gtfs_enum_type(WheelchairAccessibility)
    )
    from_trip_id: Mapped[str] = mapped_column(String, nullable=True)
    to_trip_id: Mapped[str] = mapped_column(String, nullable=True)
