from sqlalchemy import text
from sqlalchemy.orm import Session

from .models.shapes import ShapePoint
from .models.stop_times import StopTime


def vacuum(session: Session):
    session.commit()
    session.execute(text("vacuum"))
    session.commit()


def make_compact_db(session: Session):
    session.query(StopTime).delete()
    session.query(ShapePoint).delete()
    vacuum(session)
