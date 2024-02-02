from typing import List
from sqlalchemy.orm import Session
from mbta_gtfs_sqlite import MbtaGtfsArchive
from mbta_gtfs_sqlite.models import (
    RoutePattern,
    RoutePatternTypicality,
    Trip,
    ShapePoint,
)

from .config import LOCAL_ARCHIVE_PATH


def get_shape_for_route(
    session: Session,
    route_id: str,
) -> List[ShapePoint]:
    route_pattern = (
        session.query(RoutePattern)
        .filter(
            RoutePattern.route_id == route_id,
            RoutePattern.route_pattern_typicality == RoutePatternTypicality.TYPICAL,
        )
        .first()
    )
    representative_trip = (
        session.query(Trip)
        .filter(Trip.trip_id == route_pattern.representative_trip_id)
        .first()
    )
    shape_points = (
        session.query(ShapePoint)
        .filter(ShapePoint.shape_id == representative_trip.shape_id)
        .order_by(ShapePoint.shape_pt_sequence)
    ).all()
    return shape_points


def get_session_for_latest_feed() -> Session:
    archive = MbtaGtfsArchive(local_archive_path=LOCAL_ARCHIVE_PATH)
    latest_feed = archive.get_latest_feed()
    latest_feed.download_or_build()
    return latest_feed.create_sqlite_session()


if __name__ == "__main__":
    session = get_session_for_latest_feed()
    shape_points = get_shape_for_route(session, "Red")
    for point in shape_points:
        print((point.shape_pt_lat, point.shape_pt_lon))
