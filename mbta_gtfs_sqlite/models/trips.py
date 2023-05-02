from enum import Enum
from typing import Literal

from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from .routes import RouteType, TRouteType
from ..utils.enum import gtfs_enum_type


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


class BikesAllowed(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    NO_INFORMATION = "0"
    ALLOWED = "1"
    NOT_ALLOWED = "2"


TBikesAllowed = Literal[
    BikesAllowed.NO_INFORMATION,
    BikesAllowed.ALLOWED,
    BikesAllowed.NOT_ALLOWED,
]


class Trip(Base):
    route_id: Mapped[str] = mapped_column(String, index=True)
    service_id: Mapped[str] = mapped_column(String, index=True)
    trip_id: Mapped[str] = mapped_column(String)
    trip_headsign: Mapped[str] = mapped_column(String)
    trip_short_name: Mapped[str] = mapped_column(String)
    direction_id: Mapped[str] = mapped_column(String)
    block_id: Mapped[str] = mapped_column(String)
    shape_id: Mapped[str] = mapped_column(String)
    wheelchair_accessible: Mapped[TWheelchairAccessibility] = mapped_column(
        gtfs_enum_type(WheelchairAccessibility)
    )
    trip_route_type: Mapped[TRouteType] = mapped_column(gtfs_enum_type(RouteType))
    route_pattern_id: Mapped[str] = mapped_column(String, nullable=True)
    bikes_allowed: Mapped[TBikesAllowed] = mapped_column(
        gtfs_enum_type(BikesAllowed),
        nullable=True,
    )
    # start_time and end_time are not part of GTFS but they're useful information to have
    # in smaller versions of the database without StopTimes
    start_time: Mapped[int] = mapped_column(Integer)
    end_time: Mapped[int] = mapped_column(Integer)
