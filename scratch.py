from datetime import date

from archive import list_feeds_from_archive, download_feeds


def main():
    start_date = None
    feeds = list_feeds_from_archive(start_date)
    download_feeds(feeds)


if __name__ == "__main__":
    main()
