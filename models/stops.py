from enum import Enum
from typing import Literal

from sqlalchemy.types import String, Float
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base
from models.routes import RouteType, TRouteType
from utils.enum import gtfs_enum_type


class LocationType(Enum):
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
    platform_code: Mapped[str] = mapped_column(String)
    platform_name: Mapped[str] = mapped_column(String)
    stop_lat: Mapped[float] = mapped_column(Float, nullable=True)
    stop_lon: Mapped[float] = mapped_column(Float, nullable=True)
    zone_id: Mapped[str] = mapped_column(String)
    stop_address: Mapped[str] = mapped_column(String)
    stop_url: Mapped[str] = mapped_column(String)
    level_id: Mapped[str] = mapped_column(String)
    location_type: Mapped[TLocationType] = mapped_column(gtfs_enum_type(LocationType))
    parent_station: Mapped[str] = mapped_column(String)
    wheelchair_boarding: Mapped[TWheelchairBoardingType] = mapped_column(
        gtfs_enum_type(WheelchairBoardingType)
    )
    municipality: Mapped[str] = mapped_column(String)
    on_street: Mapped[str] = mapped_column(String)
    at_street: Mapped[str] = mapped_column(String)
    vehicle_type: Mapped[TRouteType] = mapped_column(gtfs_enum_type(RouteType))
