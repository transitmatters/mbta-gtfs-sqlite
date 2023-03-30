import datetime


def date_from_string(date_str: str):
    return datetime.datetime.strptime(date_str, "%Y%m%d").date()


def date_to_string(date: datetime.date):
    return date.strftime("%Y%m%d")
