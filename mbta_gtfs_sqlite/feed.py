from datetime import date
from functools import cached_property
from os import path, mkdir, remove
from shutil import copy
from zipfile import ZipFile, BadZipFile
from hashlib import md5


import requests
from tqdm import tqdm

from .utils.time import date_to_string
from .reader import GtfsReader
from .session import create_sqlalchemy_session


class GtfsFeed:
    def __init__(
        self,
        feeds_root: str,
        start_date: date,
        end_date: date,
        version: str,
        url: str,
    ):
        if not path.exists(feeds_root):
            mkdir(feeds_root)
        self.feeds_root = feeds_root
        self.start_date = start_date
        self.end_date = end_date
        self.version = version
        self.url = url

    @cached_property
    def key(self):
        return date_to_string(self.start_date)

    @cached_property
    def subdirectory(self):
        return path.join(self.feeds_root, self.key)

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
    def sqlite_compact_db_path(self):
        return self.child_by_name("gtfs_compact.sqlite3")

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
        response = requests.get(self.url, stream=True)
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        block_size = 1024
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            desc=f"Downloading {self.url}",
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
        print(f"Extracting {self.url} to {self.gtfs_subdir_path}")
        try:
            zf = ZipFile(self.gtfs_zip_path)
            zf.extractall(self.gtfs_subdir_path)
        except BadZipFile:
            print(f"Bad zip file: {self.gtfs_zip_path}")
        return target_path

    def ingest_to_db(self):
        from ingest import ingest_gtfs_csv_into_db

        try:
            self.unzip()
            target_path = self.sqlite_db_path
            if path.exists(target_path):
                return target_path
            session = create_sqlalchemy_session(target_path)
            ingest_gtfs_csv_into_db(session, self)
            return target_path
        except Exception:
            remove(target_path)
            raise

    def compactify_db(self):
        from compact import make_compact_db

        self.ingest_to_db()
        target_path = self.sqlite_compact_db_path
        if path.exists(target_path):
            return target_path
        try:
            copy(self.sqlite_db_path, target_path)
            session = create_sqlalchemy_session(target_path)
            make_compact_db(session)
        except Exception:
            remove(target_path)
            raise

    def create_all_files(self):
        # This will call other methods as necessary
        return self.compactify_db()
