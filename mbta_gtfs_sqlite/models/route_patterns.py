from enum import Enum
from typing import Literal

from sqlalchemy.types import String, Integer
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from ..utils.enum import gtfs_enum_type


class RoutePatternTypicality(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    NOT_DEFINED = "0"
    TYPICAL = "1"
    DEVIATION = "2"
    HIGHLY_ATYPICAL = "3"
    DIVERSION = "4"


TRoutePatternTypicality = Literal[
    RoutePatternTypicality.NOT_DEFINED,
    RoutePatternTypicality.TYPICAL,
    RoutePatternTypicality.DEVIATION,
    RoutePatternTypicality.HIGHLY_ATYPICAL,
    RoutePatternTypicality.DIVERSION,
]


class RoutePattern(Base):
    route_pattern_id: Mapped[str] = mapped_column(String)
    route_id: Mapped[str] = mapped_column(String, index=True)
    direction_id: Mapped[str] = mapped_column(String)
    route_pattern_name: Mapped[str] = mapped_column(String)
    route_pattern_time_desc: Mapped[str] = mapped_column(String)
    route_pattern_typicality: Mapped[TRoutePatternTypicality] = mapped_column(
        gtfs_enum_type(RoutePatternTypicality)
    )
    route_pattern_sort_order: Mapped[int] = mapped_column(Integer)
    representative_trip_id: Mapped[str] = mapped_column(String)
