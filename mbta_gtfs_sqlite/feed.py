from typing import TYPE_CHECKING, Union
from os import path, mkdir, remove, rmdir
from datetime import date
from dataclasses import dataclass
from functools import cached_property


if TYPE_CHECKING:
    from .archive import MbtaGtfsArchive

DB_FILE = "gtfs.sqlite3"
DB_COMPACT_FILE = "gtfs_compact.sqlite3"
ALL_DB_FILES = [DB_FILE, DB_COMPACT_FILE]


@dataclass
class GtfsFeed(object):
    archive: "MbtaGtfsArchive"
    key: str
    url: str
    version: str
    start_date: date
    end_date: date

    def __post_init__(self):
        self.compact_only = False

    def __repr__(self):
        return f"GtfsFeed({self.key})"

    @cached_property
    def local_subdirectory(self):
        return path.join(self.archive.local_archive_path, self.key)

    def required_feed_files(self):
        return ALL_DB_FILES if not self.compact_only else [DB_COMPACT_FILE]

    def use_compact_only(self, enabled: bool = True):
        self.compact_only = enabled

    def ensure_subdirectory(self):
        if not path.exists(self.archive.local_archive_path):
            mkdir(self.archive.local_archive_path)
        if not path.exists(self.local_subdirectory):
            mkdir(self.local_subdirectory)

    def exists_locally(self):
        for file in self.required_feed_files():
            if not path.exists(path.join(self.local_subdirectory, file)):
                return False
        return True

    def exists_remotely(self):
        try:
            remote_objects = self.archive.s3_bucket.objects.filter(Prefix=self.key)
        except RuntimeError:
            return False
        for file in self.required_feed_files():
            if not any(obj.key.endswith(file) for obj in remote_objects):
                return False
        return True

    def build_locally(self, rebuild_compact_db: bool = True, rebuild_db: bool = True):
        from .build import build_local_feed_entry

        self.ensure_subdirectory()
        build_local_feed_entry(
            self,
            compact_only=self.compact_only,
            rebuild_compact_db=rebuild_compact_db,
            rebuild_db=rebuild_db,
        )

    def download_from_s3(self):
        if not self.exists_remotely():
            raise RuntimeError("Feed does not exist remotely")
        self.ensure_subdirectory()
        for file in self.required_feed_files():
            self.archive.s3_bucket.download_file(
                f"{self.key}/{file}", path.join(self.local_subdirectory, file)
            )

    def upload_to_s3(self):
        if not self.exists_locally():
            raise RuntimeError("Feed does not exist locally")
        for file in self.required_feed_files():
            self.archive.s3_bucket.upload_file(
                path.join(self.local_subdirectory, file), f"{self.key}/{file}"
            )

    def download_or_build(self):
        if self.exists_locally():
            return
        if self.exists_remotely():
            self.download_from_s3()
            return
        self.build_locally()

    def delete_locally(self):
        if not self.exists_locally():
            raise RuntimeError("Feed does not exist locally")
        for file in self.required_feed_files():
            file_path = path.join(self.local_subdirectory, file)
            if path.exists(file_path):
                remove(file_path)
        # Delete self.local_subdirectory if empty
        try:
            rmdir(self.local_subdirectory)
        except OSError:
            pass

    def create_sqlite_session(self, compact=False):
        if not self.exists_locally():
            raise RuntimeError("Feed does not exist locally")
        from .session import create_sqlalchemy_session

        db_path = path.join(
            self.local_subdirectory,
            "gtfs_compact.sqlite3" if compact else "gtfs.sqlite3",
        )
        return create_sqlalchemy_session(db_path)

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
