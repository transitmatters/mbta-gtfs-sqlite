from datetime import date
from typing import List, Union
from csv import DictReader


import requests

from .utils.time import date_from_string
from .feed import GtfsFeed
from .config import MBTA_GTFS_ARCHIVE_URL, DEFAULT_FEEDS_ROOT


def list_feeds_from_archive(
    load_start_date: Union[date, None] = None,
    feeds_root: str = DEFAULT_FEEDS_ROOT,
    archive_url: str = MBTA_GTFS_ARCHIVE_URL,
) -> List[GtfsFeed]:
    req = requests.get(archive_url)
    lines = req.text.splitlines()
    reader = DictReader(lines, delimiter=",")
    feeds = []
    for entry in reader:
        start_date_string = entry["feed_start_date"]
        start_date = date_from_string(start_date_string)
        end_date = date_from_string(entry["feed_end_date"])
        version = entry["feed_version"]
        url = entry["archive_url"]
        if load_start_date is not None and start_date < load_start_date:
            continue
        gtfs_feed = GtfsFeed(
            feeds_root=feeds_root,
            start_date=start_date,
            end_date=end_date,
            version=version,
            url=url,
        )
        feeds.append(gtfs_feed)
    return list(sorted(feeds, key=lambda feed: feed.start_date))
