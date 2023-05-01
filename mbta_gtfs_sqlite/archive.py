from csv import DictReader
from datetime import date
from typing import Dict, Union, List

import requests

from .utils.time import date_from_string
from .utils.indexes import index_by
from .feed import GtfsFeed

MBTA_GTFS_ARCHIVE_URL = "https://cdn.mbta.com/archive/archived_feeds.txt"


class MbtaGtfsArchive(object):
    _feeds: Dict[str, GtfsFeed]

    def __init__(
        self,
        local_archive_path: str,
        s3_bucket=None,
        archive_url=MBTA_GTFS_ARCHIVE_URL,
    ):
        self.local_archive_path = local_archive_path
        self._s3_bucket = s3_bucket
        self.archive_url = archive_url
        self._load_feeds()

    @property
    def s3_bucket(self):
        if self._s3_bucket is None:
            raise RuntimeError("No S3 bucket configured for archive")
        return self._s3_bucket

    def _load_feeds(self):
        req = requests.get(self.archive_url)
        lines = req.text.splitlines()
        reader = DictReader(lines, delimiter=",")
        feeds = []
        for entry in reader:
            start_date_string = entry["feed_start_date"]
            start_date = date_from_string(start_date_string)
            end_date = date_from_string(entry["feed_end_date"])
            version = entry["feed_version"]
            url = entry["archive_url"]
            gtfs_feed = GtfsFeed(
                archive=self,
                key=start_date_string,
                start_date=start_date,
                end_date=end_date,
                version=version,
                url=url,
            )
            feeds.append(gtfs_feed)
        self._feeds = index_by(feeds, lambda f: f.key)

    def get_feed_by_key(self, key: str):
        return self._feeds.get(key)

    def get_feeds_for_dates(
        self,
        start_date: Union[None, date] = None,
        end_date: Union[None, date] = None,
    ) -> List[GtfsFeed]:
        matching_feeds = []
        for feed in self._feeds.values():
            if feed.matches_date_range(start_date=start_date, end_date=end_date):
                matching_feeds.append(feed)
        return list(sorted(matching_feeds, key=lambda feed: feed.start_date))

    def get_all_feeds(self):
        return self.get_feeds_for_dates()

    def get_feed_for_date(self, target_date: date):
        for feed in self._feeds.values():
            if target_date >= feed.start_date and target_date <= feed.end_date:
                return feed
        return None

    def get_latest_feed(self):
        return self.get_feeds_for_dates()[-1]
