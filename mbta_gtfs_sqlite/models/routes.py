from enum import Enum
from typing import Literal

from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ..utils.enum import gtfs_enum_type


class RouteType(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    TRAM = "0"
    METRO = "1"
    RAIL = "2"
    BUS = "3"
    FERRY = "4"
    CABLE_TRAM = "5"
    AERIAL_LIFT = "6"
    FUNICULAR = "7"
    TROLLEYBUS = "11"
    MONORAIL = "12"


TRouteType = Literal[
    RouteType.TRAM,
    RouteType.METRO,
    RouteType.RAIL,
    RouteType.BUS,
    RouteType.FERRY,
    RouteType.CABLE_TRAM,
    RouteType.AERIAL_LIFT,
    RouteType.FUNICULAR,
    RouteType.TROLLEYBUS,
    RouteType.MONORAIL,
]


class Route(Base):
    route_id: Mapped[str] = mapped_column(String)
    agency_id: Mapped[str] = mapped_column(String)
    route_short_name: Mapped[str] = mapped_column(String)
    route_long_name: Mapped[str] = mapped_column(String)
    route_desc: Mapped[str] = mapped_column(String)
    route_type: Mapped[TRouteType] = mapped_column(gtfs_enum_type(RouteType))
    route_url: Mapped[str] = mapped_column(String)
    route_color: Mapped[str] = mapped_column(String)
    route_text_color: Mapped[str] = mapped_column(String)
    route_sort_order: Mapped[int] = mapped_column(Integer)
    route_fare_class: Mapped[str] = mapped_column(String, nullable=True)
    line_id: Mapped[str] = mapped_column(String, index=True, nullable=True)
    listed_route: Mapped[str] = mapped_column(String, nullable=True)
