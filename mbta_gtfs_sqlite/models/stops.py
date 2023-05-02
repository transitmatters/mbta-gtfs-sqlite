from enum import Enum
from typing import Literal

from sqlalchemy.types import String, Float
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base
from .routes import RouteType, TRouteType
from ..utils.enum import gtfs_enum_type


class LocationType(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    STOP = "0"
    STATION = "1"
    ENTRANCE_EXIT = "2"
    GENERIC_NODE = "3"
    BOARDING_AREA = "4"


TLocationType = Literal[
    LocationType.STOP,
    LocationType.STATION,
    LocationType.ENTRANCE_EXIT,
    LocationType.GENERIC_NODE,
    LocationType.BOARDING_AREA,
]


class WheelchairBoardingType(Enum):
    NO_VALUE = ""  # Not in GTFS but sometimes seen
    NO_INFORMATION = "0"
    ACCESSIBLE = "1"
    NOT_ACCESSIBLE = "2"


TWheelchairBoardingType = Literal[
    WheelchairBoardingType.NO_INFORMATION,
    WheelchairBoardingType.ACCESSIBLE,
    WheelchairBoardingType.NOT_ACCESSIBLE,
]


class Stop(Base):
    stop_id: Mapped[str] = mapped_column(String)
    stop_code: Mapped[str] = mapped_column(String)
    stop_name: Mapped[str] = mapped_column(String)
    stop_desc: Mapped[str] = mapped_column(String)
    platform_code: Mapped[str] = mapped_column(String, nullable=True)
    platform_name: Mapped[str] = mapped_column(String, nullable=True)
    stop_lat: Mapped[float] = mapped_column(Float, nullable=True)
    stop_lon: Mapped[float] = mapped_column(Float, nullable=True)
    zone_id: Mapped[str] = mapped_column(String)
    stop_address: Mapped[str] = mapped_column(String, nullable=True)
    stop_url: Mapped[str] = mapped_column(String, nullable=True)
    level_id: Mapped[str] = mapped_column(String, nullable=True)
    location_type: Mapped[TLocationType] = mapped_column(
        gtfs_enum_type(LocationType),
        nullable=True,
    )
    parent_station: Mapped[str] = mapped_column(String, index=True)
    wheelchair_boarding: Mapped[TWheelchairBoardingType] = mapped_column(
        gtfs_enum_type(WheelchairBoardingType),
        nullable=True,
    )
    municipality: Mapped[str] = mapped_column(String, nullable=True)
    on_street: Mapped[str] = mapped_column(String, nullable=True)
    at_street: Mapped[str] = mapped_column(String, nullable=True)
    vehicle_type: Mapped[TRouteType] = mapped_column(
        gtfs_enum_type(RouteType), nullable=True
    )
