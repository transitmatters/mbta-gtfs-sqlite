from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, ForeignKey

from sqlalchemy.ext.declarative import declared_attr


class Base(DeclarativeBase):
    # Automatically infer each table name from the class name
    @declared_attr
    def __tablename__(cls):
        return cls.__name__

    # Provide a unique ID
    id = mapped_column(Integer, autoincrement=True, primary_key=True)

    # Basically every model is going to belong to a specific GtfsFeedInstance
    feed_info_id = mapped_column(ForeignKey("FeedInfo.id"), nullable=False, index=True)
