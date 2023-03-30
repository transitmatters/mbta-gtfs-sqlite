from sqlalchemy.orm import Session


from reader import GtfsReader


def ingest_gtfs_csv_into_session(session: Session, reader: GtfsReader):
    print("I would read", reader.root)
