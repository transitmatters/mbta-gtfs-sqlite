from datetime import date

from mbta_gtfs_sqlite.archive import MbtaGtfsArchive

archive = MbtaGtfsArchive("./feeds")
feed = archive.get_feed_for_date(date(2021, 1, 1))
feed.build_locally()
