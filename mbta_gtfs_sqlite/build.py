from dataclasses import dataclass
from os import path, remove
from shutil import copy
from zipfile import ZipFile
from hashlib import md5


import requests

from .reader import GtfsReader
from .feed import GtfsFeed


@dataclass
class GtfsFeedDownloadResult(object):
    url: str
    zip_md5_checksum: str


def download_feed_zip(feed_url: str, target_path: str):
    response = requests.get(feed_url, stream=True)
    block_size = 1024
    with open(target_path, "wb") as file:
        for data in response.iter_content(block_size):
            file.write(data)


def unzip_feed(zip_path: str, target_path: str):
    zf = ZipFile(zip_path)
    zf.extractall(target_path)


def get_zip_checksum(zip_path: str) -> str:
    with open(zip_path, "rb") as file:
        chunk_size = 4096
        hasher = md5()
        while chunk := file.read(chunk_size):
            hasher.update(chunk)
    checksum = hasher.hexdigest()
    return checksum


def ingest_feed_to_sqlite(
    feed_path: str,
    db_path: str,
    compact_db_path: str,
    result: GtfsFeedDownloadResult,
):
    from .ingest import ingest_gtfs_csv_into_db
    from .compact import make_compact_db
    from .session import create_sqlalchemy_session

    try:
        reader = GtfsReader(feed_path)
        session = create_sqlalchemy_session(db_path)
        ingest_gtfs_csv_into_db(session, result, reader)
        copy(db_path, compact_db_path)
        compact_session = create_sqlalchemy_session(compact_db_path)
        make_compact_db(compact_session)
    except Exception as ex:
        try:
            remove(db_path)
            remove(compact_db_path)
        except FileNotFoundError:
            pass
        raise ex


def build_local_feed_entry(feed: GtfsFeed, compact_only=False):
    (zip_path, feed_path, db_path, compact_db_path) = (
        path.join(feed.local_subdirectory, entity)
        for entity in ("data.zip", "feed", "gtfs.sqlite3", "gtfs_compact.sqlite3")
    )
    download_feed_zip(feed.url, zip_path)
    unzip_feed(zip_path, feed_path)
    result = GtfsFeedDownloadResult(
        url=feed.url,
        zip_md5_checksum=get_zip_checksum(zip_path),
    )
    ingest_feed_to_sqlite(feed_path, db_path, compact_db_path, result)
    if compact_only:
        remove(db_path)
