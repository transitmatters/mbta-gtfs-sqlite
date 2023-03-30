from sqlalchemy.orm import Session
from typing import Dict, Any, Callable, Type, Generator

from archive import GtfsFeedDownload
from utils.time import date_from_string, seconds_from_string
from models.base import Base
from models.calendar_attributes import CalendarAttribute
from models.calendar_dates import CalendarServiceException
from models.calendar import CalendarService
from models.feed_info import FeedInfo
from models.lines import Line
from models.route_patterns import RoutePattern
from models.routes import Route
from models.shapes import ShapePoint
from models.stops import Stop
from models.stop_times import StopTime
from models.transfers import Transfer
from models.trips import Trip

RowTransform = Callable[[str], any]
RowTransforms = Dict[str, RowTransform]


def nullable(transform: RowTransform) -> RowTransform:
    def inner_transform(val: str):
        if not val:
            return None
        return transform(val)

    return inner_transform


def transform_row_dict(
    row_dict: Dict[str, str],
    transforms: RowTransforms,
) -> Dict[str, Any]:
    return {
        key: (transforms[key](value) if transforms.get(key) else value)
        for key, value in row_dict.items()
    }


def ingest_feed_info(session: Session, download: GtfsFeedDownload) -> FeedInfo:
    num_feed_infos = session.query(FeedInfo).count()
    next_id = 1 + num_feed_infos
    feed_info_dict_raw = next(download.reader.read_feed_info())
    feed_info_dict = transform_row_dict(
        {
            **feed_info_dict_raw,
            "id": next_id,
            "feed_info_id": next_id,
            "retrieved_from_url": download.feed.remote_url,
            "zip_md5_checksum": download.zip_md5_checksum,
        },
        {
            "feed_start_date": date_from_string,
            "feed_end_date": date_from_string,
        },
    )
    feed_info = FeedInfo(**feed_info_dict)
    session.add(feed_info)
    session.commit()
    return feed_info


def ingest_rows(
    session: Session,
    model: Type[Base],
    feed_info: FeedInfo,
    rows: Generator[Dict[str, str], None, None],
    transforms: RowTransforms = {},
):
    mappings = [
        {
            **transform_row_dict(row, transforms),
            "feed_info_id": feed_info.id,
        }
        for row in rows()
    ]
    session.bulk_insert_mappings(model, mappings)


def ingest_gtfs_csv_into_session(session: Session, download: GtfsFeedDownload):
    reader = download.reader
    feed_info = ingest_feed_info(session, download)
    ingest_rows(
        session=session,
        model=CalendarService,
        feed_info=feed_info,
        rows=reader.read_calendar,
        transforms={
            "start_date": date_from_string,
            "end_date": date_from_string,
        },
    )
    ingest_rows(
        session=session,
        model=CalendarServiceException,
        feed_info=feed_info,
        rows=reader.read_calendar_dates,
        transforms={
            "date": date_from_string,
        },
    )
    ingest_rows(
        session=session,
        model=CalendarAttribute,
        feed_info=feed_info,
        rows=reader.read_calendar_attributes,
        transforms={
            "rating_start_date": nullable(date_from_string),
            "rating_end_date": nullable(date_from_string),
        },
    )
    ingest_rows(
        session=session,
        model=Line,
        feed_info=feed_info,
        rows=reader.read_lines,
    )
    ingest_rows(
        session=session,
        model=Route,
        feed_info=feed_info,
        rows=reader.read_routes,
    )
    ingest_rows(
        session=session,
        model=RoutePattern,
        feed_info=feed_info,
        rows=reader.read_route_patterns,
    )
    ingest_rows(
        session=session,
        model=ShapePoint,
        feed_info=feed_info,
        rows=reader.read_shapes,
        transforms={
            "shape_pt_lat": float,
            "shape_pt_lon": float,
            "shape_pt_sequence": int,
            "shape_dist_traveled": nullable(float),
        },
    )
    ingest_rows(
        session=session,
        model=Stop,
        feed_info=feed_info,
        rows=reader.read_stops,
        transforms={
            "stop_lat": nullable(float),
            "stop_lon": nullable(float),
        },
    )
    ingest_rows(
        session=session,
        model=Transfer,
        feed_info=feed_info,
        rows=reader.read_transfers,
        transforms={
            "min_transfer_time": nullable(int),
            "min_walk_time": nullable(int),
            "min_wheelchair_time": nullable(int),
            "suggested_buffer_time": nullable(int),
        },
    )
    ingest_rows(
        session=session,
        model=Trip,
        feed_info=feed_info,
        rows=reader.read_trips,
    )
    ingest_rows(
        session=session,
        model=StopTime,
        feed_info=feed_info,
        rows=reader.read_stop_times,
        transforms={
            "arrival_time": seconds_from_string,
            "departure_time": seconds_from_string,
            "stop_sequence": int,
        },
    )
    session.commit()
