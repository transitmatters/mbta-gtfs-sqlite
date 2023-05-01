from csv import DictReader
from os import path


class GtfsReader:
    def _reader_by_file_name(self, name: str):
        file_path = path.join(self.root, name + ".txt")

        def load():
            try:
                with open(file_path, "r") as file:
                    dict_reader = DictReader(file)
                    for row in dict_reader:
                        yield row
            except FileNotFoundError:
                yield from []

        return load

    def __init__(self, root: str):
        self.root = root
        self.read_calendar = self._reader_by_file_name("calendar")
        self.read_calendar_attributes = self._reader_by_file_name("calendar_attributes")
        self.read_calendar_dates = self._reader_by_file_name("calendar_dates")
        self.read_feed_info = self._reader_by_file_name("feed_info")
        self.read_lines = self._reader_by_file_name("lines")
        self.read_route_patterns = self._reader_by_file_name("route_patterns")
        self.read_routes = self._reader_by_file_name("routes")
        self.read_shapes = self._reader_by_file_name("shapes")
        self.read_stop_times = self._reader_by_file_name("stop_times")
        self.read_stops = self._reader_by_file_name("stops")
        self.read_transfers = self._reader_by_file_name("transfers")
        self.read_trips = self._reader_by_file_name("trips")
