from typing import TYPE_CHECKING, Union
from os import path
from datetime import date
from dataclasses import dataclass
from functools import cached_property


if TYPE_CHECKING:
    from .archive import MbtaGtfsArchive

FEED_FILES = [
    "gtfs.sqlite3",
    "gtfs_compact.sqlite3",
]


@dataclass
class GtfsFeed(object):
    archive: "MbtaGtfsArchive"
    key: str
    url: str
    version: str
    start_date: date
    end_date: date

    def __post_init__(self):
        self.exists_locally = self._check_exists_locally()

    def __repr__(self):
        return f"GtfsFeed({self.key})"

    @cached_property
    def local_subdirectory(self):
        return path.join(self.archive.local_archive_path, self.key)

    def _check_exists_locally(self):
        for file in FEED_FILES:
            if not path.exists(path.join(self.local_subdirectory, file)):
                return False
        return True

    def build_locally(self):
        from .build import build_local_feed_entry

        build_local_feed_entry(self)
        self.exists_locally = self._check_exists_locally()

    def matches_date_range(
        self,
        start_date: Union[None, date],
        end_date: Union[None, date],
    ):
        if start_date is None and end_date is None:
            return True
        if start_date is None:
            return end_date >= self.start_date
        if end_date is None:
            return self.end_date >= start_date
        return end_date >= self.start_date and self.end_date >= start_date
