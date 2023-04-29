from sqlalchemy import text
from sqlalchemy.orm import Session

from models.stop_times import StopTime

def vacuum(session: Session):
    session.commit()
    session.execute(text("vacuum"))
    session.commit()


def remove_stop_times(session: Session):
    session.query(StopTime).delete()
    vacuum(session)
