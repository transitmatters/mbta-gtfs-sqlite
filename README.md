# `mbta-gtfs-sqlite`

```
pip install mbta-gtfs-sqlite
```

A Python package to simplify working with the MBTA's archive of historical and current GTFS feeds. The MBTA provides this as a [CSV index](https://cdn.mbta.com/archive/archived_feeds.txt) of zipfile URLs which in turn contain static GTFS bundles — see the documentation on [GTFS in general](https://gtfs.org/schedule/reference/) and the [MBTA's own flavor](https://github.com/mbta/gtfs-documentation).


This tool can help you:

- Maintain a local index of the MBTA's GTFS feeds in sqlite format
- Query feeds using an ORM schema built on [SQLAlchemy](https://www.sqlalchemy.org/)
- Build a remote mirror of your index on S3

## Structure of the archive

The library will populate a local directory with a structure like this:

```
my-feeds/
    20210104/
    20210108/
    20210113/
        feed/
        data.zip
        gtfs.sqlite3
        gtfs_compact.sqlite3
```

The subdirectory names are `keys` — string representation of feed start dates. Inside you'll find the following items:

- `gtfs.sqlite3`: a full sqlite representation of the feed
- `gtfs_compact.sqlite3`: a smaller sqlite representation of the feed with the large `StopTimes` table removed.
- `data.zip`: the zipped version of the raw GTFS feed, straight from the MBTA
- `feed`: an unzipped version of the raw GTFS feed

If you provide an S3 bucket, this path structure will be mirrored remotely. However, the library does not upload `feed/` or `data.zip` to S3 — these are considered intermediate build artifacts that are useful for debugging purposes.

## Retrieving the archive

The `MbtaGtfsArchive` class serves as the entrypoint to the MBTA's archive:

```py
>>> from mbta_gtfs_sqlite import MbtaGtfsArchive
>>> archive = MbtaGtfsArchive("~/gtfs-feeds")
>>> archive.get_all_feeds()
[GtfsFeed(20090313), GtfsFeed(20090403), ...]
```

Its methods all return `GtfsFeed` objects (explained below). These have a `key`, which is a string  of the feed's effective start date (like `20210403`).

### `MbtaGtfsArchive`

```py
# Constructor
MbtaGtfsArchive(
    # A directory on your machine to hold GTFS feeds
    local_archive_path: str,
    # An optional S3 bucket to read/write feeds to
    s3_bucket: Union[None, boto3.Bucket] = None,
    # An optional, alternative URL for the MBTA's index of historical feeds
    # The current URL is hard-coded and there's probably no reason to change it.
    archive_url: Union[None, str] = None,
)

# Returns a feed with a specific key, if one exists
get_feed_by_key(key: str) -> Union[None, GtfsFeed]

# Returns all feeds active within a specified date range (in chronological order)
get_feeds_for_dates(
    start_date: Union[None, date] = None,
    end_date: Union[None, date] = None,
) -> List[GtfsFeed]

# Returns all feeds
get_all_feeds() -> List[GtfsFeed]

# Returns the feed that was active on a specific date
get_feed_for_date(target_date: date) -> Union[None, GtfsFeed]

# Returns the latest feed
get_latest_feed() -> GtfsFeed
```

### `GtfsFeed`

...has these basic properties:

```py
# A date key like "20210403"
key: str
# The start of this feed's effective range
start_date: str
# The end of this feed's effective range
end_date: str
# A string provided by the MBTA with more info about this feed
version: str
# The remote URL of this feed
url: str
```

It has methods to check whether a feed is available locally or remotely:

```py
# Determines whether there's a complete local copy of the feed in local_archive_path
exists_locally() -> bool

# Determines whether there's a complete remote copy of the feed in s3_bucket
exists_remotely() -> bool
```

To get a copy of the feed you can use these methods:

```py
# Download a zip from the MBTA and create sqlite databases locally
build_locally()

# Download a version of this feed from s3_bucket
# Throws a RuntimeException if exists_remotely() is false.
download_from_s3()

# Downloads the sqlite representations of this feed from S3 if they're available
# Otherwise builds them locally. Does nothing if the feed is already present locally.
download_or_build()
```

To write a copy of the feed to S3 you can:

```py
# Uploads the sqlite representations of this feed to S3.
# Throws a RuntimeException if exists_locally() is false.
upload_to_s3()
```

With a local copy of the feed in hand, you can create a SQLAlchemy session to work with its data:

```py
# Creates a SQLAlchemy session for this feed.
# Throws a RuntimeException if exists_locally() is false.
create_sqlite_session(
    # If true, will use the gtfs_compact version of the db (without StopTimes)
    compact: bool,
) -> sqlalchemy.orm.Session
```

# A complete example

```py
import boto3
from mbta_gtfs_sqlite import MbtaGtfsArchive
from mbta_gtfs_sqlite.models import Route

path_to_feeds = "~/gtfs-feeds"

s3 = boto3.resource(
    "s3",
    aws_access_key_id="my-access-key-id",
    aws_secret_access_key="my-secret-access-key",
)

archive = MbtaGtfsArchive(
    local_archive_path=path_to_feeds,
    s3_bucket=s3.Bucket("my-gtfs-bucket"),
)

latest_feed = archive.get_latest_feed()
latest_feed.download_or_build()
assert latest_feed.exists_locally()

session = latest_feed.create_sqlite_session
all_routes = session.query(Route).all()
```

Please refer to the `models/` subdirectory for the database schema, and the [SQLAlchemy documentation](https://www.sqlalchemy.org/) for more info on how to query it.
