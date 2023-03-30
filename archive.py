from dataclasses import dataclass
from datetime import date
from functools import cached_property
from os import path, mkdir
from typing import List
from csv import DictReader
from zipfile import ZipFile, BadZipFile
from hashlib import md5


import requests
from tqdm import tqdm

from utils.decorators import listify
from utils.time import date_to_string, date_from_string
from reader import GtfsReader
from session import create_sqlalchemy_session_for_file
from config import DEFAULT_FEEDS_ROOT, MBTA_GTFS_ARCHIVE_URL


@dataclass
class GtfsFeed:
    start_date: date
    end_date: date
    version: str
    remote_url: str


@dataclass
class GtfsFeedDownload:
    feed: GtfsFeed
    local_base_path: str

    @cached_property
    def subdirectory(self):
        return path.join(self.local_base_path, date_to_string(self.feed.start_date))

    def child_by_name(self, filename):
        return path.join(self.subdirectory, filename)

    @cached_property
    def gtfs_zip_path(self):
        return self.child_by_name("data.zip")

    @cached_property
    def gtfs_subdir_path(self):
        return self.child_by_name("feed")

    @cached_property
    def sqlite_db_path(self):
        return self.child_by_name("gtfs.sqlite3")

    @cached_property
    def reader(self):
        return GtfsReader(root=self.gtfs_subdir_path)

    @cached_property
    def zip_md5_checksum(self):
        self.download_gtfs_zip()
        with open(self.gtfs_zip_path, "rb") as file:
            chunk_size = 4096
            hasher = md5()
            while chunk := file.read(chunk_size):
                hasher.update(chunk)
        checksum = hasher.hexdigest()
        return checksum

    def ensure_subdirectory(self):
        if not path.exists(self.subdirectory):
            mkdir(self.subdirectory)

    def download_gtfs_zip(self) -> str:
        self.ensure_subdirectory()
        target_path = self.gtfs_zip_path
        if path.exists(target_path):
            return target_path
        if not path.exists(self.local_base_path):
            mkdir(self.local_base_path)
        response = requests.get(self.feed.remote_url, stream=True)
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            desc=f"Downloading {self.feed.remote_url}",
        )
        with open(target_path, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        return target_path

    def unzip(self) -> str:
        self.download_gtfs_zip()
        target_path = self.gtfs_subdir_path
        if path.exists(target_path):
            return
        print(f"Extracting {self.feed.remote_url} to {self.gtfs_subdir_path}")
        try:
            zf = ZipFile(self.gtfs_zip_path)
            zf.extractall(self.gtfs_subdir_path)
        except BadZipFile:
            print(f"Bad zip file: {self.gtfs_zip_path}")
        return target_path

    def ingest_to_db(self):
        from ingest import ingest_gtfs_csv_into_session

        self.unzip()
        target_path = self.sqlite_db_path
        if path.exists(target_path):
            return target_path
        session = create_sqlalchemy_session_for_file(self.sqlite_db_path)
        ingest_gtfs_csv_into_session(session, self)
        return target_path


@listify
def list_feeds_from_archive(
    load_start_date: date,
    archive_url: str = MBTA_GTFS_ARCHIVE_URL,
) -> List[GtfsFeed]:
    req = requests.get(archive_url)
    lines = req.text.splitlines()
    reader = DictReader(lines, delimiter=",")
    for entry in reader:
        start_date = date_from_string(entry["feed_start_date"])
        end_date = date_from_string(entry["feed_end_date"])
        version = entry["feed_version"]
        url = entry["archive_url"]
        if start_date < load_start_date:
            continue
        gtfs_feed = GtfsFeed(
            start_date=start_date,
            end_date=end_date,
            version=version,
            remote_url=url,
        )
        yield gtfs_feed


def download_feeds(
    feeds: List[GtfsFeed],
    into_directory: str = DEFAULT_FEEDS_ROOT,
) -> List[GtfsFeedDownload]:
    if not path.exists(into_directory):
        mkdir(into_directory)
    for feed in feeds:
        download = GtfsFeedDownload(feed, into_directory)
        download.ingest_to_db()
