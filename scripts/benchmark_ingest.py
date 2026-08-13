"""
Benchmarks mbta_gtfs_sqlite.build.ingest_feed_to_sqlite against a real MBTA GTFS feed,
reporting wall time and peak RSS.

Usage:
    python3 scripts/benchmark_ingest.py
    python3 scripts/benchmark_ingest.py --refetch  # force a fresh download of the feed

The feed is downloaded once into feeds/benchmark/ (gitignored) and reused on
subsequent runs.
"""

import argparse
import os
import resource
import sys
import time

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

from mbta_gtfs_sqlite.build import (  # noqa: E402
    GtfsFeedDownloadResult,
    download_feed_zip,
    get_zip_checksum,
    ingest_feed_to_sqlite,
    unzip_feed,
)
from mbta_gtfs_sqlite.feed import DEFAULT_INGEST_BATCH_SIZE  # noqa: E402

GTFS_URL = "https://cdn.mbta.com/MBTA_GTFS.zip"
WORK_DIR = os.path.join(REPO_ROOT, "feeds", "benchmark")


def fetch_feed(work_dir: str, refetch: bool):
    zip_path = os.path.join(work_dir, "data.zip")
    feed_path = os.path.join(work_dir, "feed")
    if refetch or not os.path.exists(feed_path):
        os.makedirs(work_dir, exist_ok=True)
        print(f"Downloading {GTFS_URL} ...")
        download_feed_zip(GTFS_URL, zip_path)
        os.makedirs(feed_path, exist_ok=True)
        unzip_feed(zip_path, feed_path)
    else:
        print(
            f"Reusing cached feed at {feed_path} (pass --refetch to force a re-download)"
        )
    return zip_path, feed_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refetch",
        action="store_true",
        help="Force a fresh download of the GTFS feed instead of reusing the cached copy",
    )
    args = parser.parse_args()

    zip_path, feed_path = fetch_feed(WORK_DIR, args.refetch)

    db_path = os.path.join(WORK_DIR, "gtfs.sqlite3")
    if os.path.exists(db_path):
        os.remove(db_path)

    result = GtfsFeedDownloadResult(
        url=GTFS_URL, zip_md5_checksum=get_zip_checksum(zip_path)
    )

    t0 = time.perf_counter()
    ingest_feed_to_sqlite(feed_path, db_path, result, DEFAULT_INGEST_BATCH_SIZE)
    elapsed = time.perf_counter() - t0

    # ru_maxrss is peak RSS in KB on Linux, bytes on macOS.
    peak_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        peak_rss_kb //= 1024

    print(f"ingest_feed_to_sqlite: {elapsed:.1f}s")
    print(f"peak RSS: {peak_rss_kb / 1e6:.2f} GB ({peak_rss_kb:,} KB)")
    print(f"gtfs.sqlite3 size: {os.path.getsize(db_path) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
