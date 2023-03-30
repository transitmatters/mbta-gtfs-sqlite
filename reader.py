from csv import DictReader
from os import path


class GtfsReader:
    def _reader_by_file_name(self, name: str):
        file_path = path.join(self.root, name + ".txt")

        def load():
            with open(file_path, "r") as file:
                print(f"Reading {file_path}...")
                dict_reader = DictReader(file)
                for row in dict_reader:
                    yield row

        return load

    def __init__(self, root: str):
        self.root = root
        self.load_calendar = self._reader_by_file_name("calendar")
        self.load_calendar_attributes = self._reader_by_file_name("calendar_attributes")
        self.load_calendar_dates = self._reader_by_file_name("calendar_dates")
        self.load_stop_times = self._reader_by_file_name("stop_times")
        self.load_stops = self._reader_by_file_name("stops")
        self.load_transfers = self._reader_by_file_name("transfers")
        self.load_trips = self._reader_by_file_name("trips")
        self.load_routes = self._reader_by_file_name("routes")
        self.load_route_patterns = self._reader_by_file_name("route_patterns")
        self.load_shapes = self._reader_by_file_name("shapes")
        self.load_lines = self._reader_by_file_name("lines")
