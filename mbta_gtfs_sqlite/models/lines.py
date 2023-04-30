from sqlalchemy.types import String
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Line(Base):
    line_id: Mapped[str] = mapped_column(String)
    line_short_name: Mapped[str] = mapped_column(String)
    line_long_name: Mapped[str] = mapped_column(String)
    line_desc: Mapped[str] = mapped_column(String)
    line_url: Mapped[str] = mapped_column(String)
    line_color: Mapped[str] = mapped_column(String)
    line_text_color: Mapped[str] = mapped_column(String)
    line_sort_order: Mapped[str] = mapped_column(String)
