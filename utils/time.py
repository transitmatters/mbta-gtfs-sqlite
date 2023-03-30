import datetime


def date_from_string(date_str: str):
    return datetime.datetime.strptime(date_str, "%Y%m%d").date()


def date_to_string(date: datetime.date):
    return date.strftime("%Y%m%d")


def timedelta_from_string(time_str: str):
    pieces = [int(x) for x in time_str.split(":")]
    if len(pieces) == 3:
        hours, minutes, seconds = pieces
        return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    hours, minutes = pieces
    return datetime.timedelta(hours=hours, minutes=minutes)


def seconds_from_string(time_str: str):
    td = timedelta_from_string(time_str)
    return int(td.total_seconds())
