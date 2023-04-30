from sqlalchemy.types import String, Integer, Float
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class ShapePoint(Base):
    shape_id: Mapped[str] = mapped_column(String, index=True)
    shape_pt_lat: Mapped[float] = mapped_column(Float)
    shape_pt_lon: Mapped[float] = mapped_column(Float)
    shape_pt_sequence: Mapped[int] = mapped_column(Integer)
    shape_dist_traveled: Mapped[float] = mapped_column(Float, nullable=True)
