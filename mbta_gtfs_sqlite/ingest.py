from sqlalchemy.orm import Session
from typing import Dict, Any, Callable, Type, Iterable, Union
from more_itertools import ichunked

from .build import GtfsFeedDownloadResult
from .reader import GtfsReader
from .utils.time import date_from_string, seconds_from_string
from .models.agency import Agency
from .models.base import Base
from .models.calendar_attributes import CalendarAttribute
from .models.calendar_dates import CalendarServiceException
from .models.calendar import CalendarService
from .models.feed_info import FeedInfo
from .models.lines import Line
from .models.route_patterns import RoutePattern
from .models.routes import Route
from .models.shapes import ShapePoint
from .models.stops import Stop
from .models.stop_times import StopTime
from .models.transfers import Transfer
from .models.trips import Trip

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
    model: Type[Base],
) -> Dict[str, Any]:
    return {
        key: (transforms[key](value) if transforms.get(key) else value)
        for key, value in row_dict.items()
        if key in model.__table__.columns
    }


def get_trip_extra_fields_by_trip_id(
    stop_time_rows: Iterable[Dict[str, str]],
) -> Dict[str, Dict[str, Any]]:
    extra_fields_by_trip_id: Dict[str, Dict[str, Any]] = {}
    for stop_time_row in stop_time_rows:
        trip_id = stop_time_row["trip_id"]
        stop_sequence = int(stop_time_row["stop_sequence"])
        arrival_time = stop_time_row["arrival_time"]
        extra_fields = extra_fields_by_trip_id.get(trip_id)
        if extra_fields is None:
            extra_fields_by_trip_id[trip_id] = {
                "min_stop_sequence": stop_sequence,
                "start_time": arrival_time,
                "max_stop_sequence": stop_sequence,
                "end_time": arrival_time,
                "stop_count": 1,
            }
            continue
        extra_fields["stop_count"] += 1
        if stop_sequence < extra_fields["min_stop_sequence"]:
            extra_fields["min_stop_sequence"] = stop_sequence
            extra_fields["start_time"] = arrival_time
        if stop_sequence > extra_fields["max_stop_sequence"]:
            extra_fields["max_stop_sequence"] = stop_sequence
            extra_fields["end_time"] = arrival_time
    return extra_fields_by_trip_id


def ingest_feed_info(
    session: Session,
    download: GtfsFeedDownloadResult,
    reader: GtfsReader,
) -> FeedInfo:
    num_feed_infos = session.query(FeedInfo).count()
    next_id = 1 + num_feed_infos
    feed_info_dict_raw = next(reader.read_feed_info())
    feed_info_dict = transform_row_dict(
        {
            **feed_info_dict_raw,
            "id": next_id,
            "feed_info_id": next_id,
            "retrieved_from_url": download.url,
            "zip_md5_checksum": download.zip_md5_checksum,
        },
        {
            "feed_start_date": date_from_string,
            "feed_end_date": date_from_string,
        },
        FeedInfo,
    )
    feed_info = FeedInfo(**feed_info_dict)
    session.add(feed_info)
    session.commit()
    return feed_info


def ingest_rows(
    session: Session,
    model: Type[Base],
    feed_info: FeedInfo,
    rows: Iterable[Dict[str, str]],
    batch_size: Union[None, int],
    transforms: RowTransforms = {},
):
    if batch_size:
        batches = ichunked(rows, batch_size)
    else:
        batches = [rows]
    for batch in batches:
        mappings = (
            {
                **transform_row_dict(row, transforms, model),
                "feed_info_id": feed_info.id,
            }
            for row in batch
        )
        session.bulk_insert_mappings(model, mappings)


def get_augmented_trip_rows(reader: GtfsReader) -> Iterable[Dict[str, str]]:
    extra_fields_by_trip_id = get_trip_extra_fields_by_trip_id(reader.read_stop_times())
    for trip_row in reader.read_trips():
        extra_fields = extra_fields_by_trip_id[trip_row["trip_id"]]
        yield {
            **trip_row,
            "start_time": extra_fields["start_time"],
            "end_time": extra_fields["end_time"],
            "stop_count": extra_fields["stop_count"],
        }


def ingest_gtfs_csv_into_db(
    session: Session,
    download: GtfsFeedDownloadResult,
    reader: GtfsReader,
    batch_size: Union[None, int] = None,
):
    feed_info = ingest_feed_info(session, download, reader)
    ingest_rows(
        session=session,
        model=Agency,
        feed_info=feed_info,
        rows=reader.read_agency(),
        batch_size=batch_size,
    )
    ingest_rows(
        session=session,
        model=CalendarService,
        feed_info=feed_info,
        rows=reader.read_calendar(),
        batch_size=batch_size,
        transforms={
            "start_date": date_from_string,
            "end_date": date_from_string,
        },
    )
    ingest_rows(
        session=session,
        model=CalendarServiceException,
        feed_info=feed_info,
        rows=reader.read_calendar_dates(),
        batch_size=batch_size,
        transforms={
            "date": date_from_string,
        },
    )
    ingest_rows(
        session=session,
        model=CalendarAttribute,
        feed_info=feed_info,
        rows=reader.read_calendar_attributes(),
        batch_size=batch_size,
        transforms={
            "rating_start_date": nullable(date_from_string),
            "rating_end_date": nullable(date_from_string),
        },
    )
    ingest_rows(
        session=session,
        model=Line,
        feed_info=feed_info,
        rows=reader.read_lines(),
        batch_size=batch_size,
    )
    ingest_rows(
        session=session,
        model=Route,
        feed_info=feed_info,
        rows=reader.read_routes(),
        batch_size=batch_size,
    )
    ingest_rows(
        session=session,
        model=RoutePattern,
        feed_info=feed_info,
        rows=reader.read_route_patterns(),
        batch_size=batch_size,
    )
    ingest_rows(
        session=session,
        model=ShapePoint,
        feed_info=feed_info,
        rows=reader.read_shapes(),
        batch_size=batch_size,
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
        rows=reader.read_stops(),
        batch_size=batch_size,
        transforms={
            "stop_lat": nullable(float),
            "stop_lon": nullable(float),
        },
    )
    ingest_rows(
        session=session,
        model=Transfer,
        feed_info=feed_info,
        rows=reader.read_transfers(),
        batch_size=batch_size,
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
        rows=get_augmented_trip_rows(reader),
        batch_size=batch_size,
        transforms={
            "start_time": seconds_from_string,
            "end_time": seconds_from_string,
        },
    )
    ingest_rows(
        session=session,
        model=StopTime,
        feed_info=feed_info,
        rows=reader.read_stop_times(),
        batch_size=batch_size,
        transforms={
            "arrival_time": seconds_from_string,
            "departure_time": seconds_from_string,
            "stop_sequence": int,
        },
    )
    session.commit()
