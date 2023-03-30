from enum import Enum
from typing import Literal

from sqlalchemy.types import String
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base
from models.routes import RouteType, TRouteType
from utils.enum import gtfs_enum_type


class WheelchairAccessibility(Enum):
    NO_INFORMATION = "0"
    ACCESSIBLE = "1"
    NOT_ACCESSIBLE = "2"


TWheelchairAccessibility = Literal[
    WheelchairAccessibility.NO_INFORMATION,
    WheelchairAccessibility.ACCESSIBLE,
    WheelchairAccessibility.NOT_ACCESSIBLE,
]


class BikesAllowed(Enum):
    NO_INFORMATION = "0"
    ALLOWED = "1"
    NOT_ALLOWED = "2"


TBikesAllowed = Literal[
    BikesAllowed.NO_INFORMATION,
    BikesAllowed.ALLOWED,
    BikesAllowed.NOT_ALLOWED,
]


class Trip(Base):
    route_id: Mapped[str] = mapped_column(String)
    service_id: Mapped[str] = mapped_column(String)
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
    route_pattern_id: Mapped[str] = mapped_column(String)
    bikes_allowed: Mapped[TBikesAllowed] = mapped_column(gtfs_enum_type(BikesAllowed))
