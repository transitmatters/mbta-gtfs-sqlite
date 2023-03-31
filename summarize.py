from typing import List, Dict, Callable, Union, Any

from tqdm import tqdm
from sqlalchemy import text
from sqlalchemy.orm import Session

from utils.time import seconds_from_string
from models.stop_times import StopTime
from models.trips import Trip
from models.trip_summary import TripSummary


def bucket_by(
    items: List[any], key_getter: Union[str, Callable[[Any], str]],
) -> Dict[str, List[any]]:
    res = {}
    if isinstance(key_getter, str):
        key_getter_as_str = key_getter
        key_getter = lambda dict: dict[key_getter_as_str]
    for item in items:
        key = key_getter(item)
        res.setdefault(key, [])
        res[key].append(item)
    return res


def vacuum(session: Session):
    session.commit()
    session.execute(text("vacuum"))
    session.commit()


# This probably only works on databases containing only a single feed
def create_trip_summaries(session: Session):
    chunk_size = 1000
    trips = session.query(Trip).all()
    trip_ids = [t.trip_id for t in trips]
    trip_id_chunks = [
        trip_ids[i : i + chunk_size] for i in range(0, len(trips), chunk_size)
    ]
    for trip_ids_in_chunk in tqdm(trip_id_chunks, desc="Summarizing trips..."):
        stop_times = (
            session.query(StopTime)
            .filter(StopTime.trip_id.in_(trip_ids_in_chunk))
            .all()
        )
        stop_times_by_trip_id = bucket_by(stop_times, lambda st: st.trip_id)
        trip_summaries_mappings = []
        for trip_id, stop_times in stop_times_by_trip_id.items():
            stop_times_sorted = list(
                sorted(stop_times, key=lambda st: st.stop_sequence)
            )
            first, last = stop_times_sorted[0], stop_times_sorted[-1]
            trip_summaries_mappings.append(
                {
                    "feed_info_id": first.feed_info_id,
                    "trip_id": trip_id,
                    "start_time": first.departure_time,
                    "end_time": last.arrival_time,
                }
            )
        session.bulk_insert_mappings(TripSummary, trip_summaries_mappings)
    session.commit()


def summarize_db(session: Session):
    create_trip_summaries(session)
    session.query(StopTime).delete()
    vacuum(session)
