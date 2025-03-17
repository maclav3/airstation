import measurements
from measurements import DataPoint, Timestamp, DataSeries
import os


class DB:
    def __init__(self, path: str, columns: list[measurements.DataColumn] = None):
        self._path = path
        if not columns:
            columns = measurements.supported_data_columns
        self.data_series = measurements.DataSeries(columns, [])

        try:
            os.stat(path)
        except OSError:
            # create file if it does not exist
            with open(path, "w") as f:
                f.write(self.data_series.csv_header())

    def insert(self, data: DataPoint):
        with open(self._path, "a") as f:
            f.write(data.to_csv())

    def read(
        self, from_timestamp: Timestamp | None, to_timestamp: Timestamp | None,
    ) -> DataSeries:
        """read data points from the database between the given timestamps"""
        _ds = DataSeries(self.data_series.columns, [])

        if from_timestamp is None:
            _from_offset = self.data_series.header_length() + 1
        else:
            _from_offset = self._find_timestamp_offset(from_timestamp)

        if to_timestamp is None:
            _to_offset = self._file_size()
        else:
            _to_offset = self._find_timestamp_offset(to_timestamp)

        if _from_offset == -1 or _to_offset == -1:
            return _ds

        with open(self._path, "r") as f:
            f.seek(_from_offset)
            while f.tell() < _to_offset and f.tell() < self._file_size():
                _line = f.readline()
                dp = DataPoint.from_csv(_line, self.data_series.csv_header())
                _ds.append(dp)

        return _ds

    def _file_size(self) -> int:
        return os.stat(self._path).st_size

    def _find_timestamp_offset(self, look_for: Timestamp) -> int:
        """find the offset of the line with the given timestamp using binary search"""
        _low = self._header_length
        _high = self._file_size()

        with open(self._path, "r") as f:
            _last = self._read_timestamp(f, _high - self._record_length + 1)
            if look_for >= _last:
                return _high

            _first = self._read_timestamp(f, self._header_length)
            if look_for <= _first:
                return self._header_length

            # rewind to first record
            f.seek(self._header_length)

            while _low < _high:
                _mid = (_low + _high) // 2
                _mid = self._align_to_record(_mid)

                ts = self._read_timestamp(f, _mid)
                if ts == look_for or _high - _low < self._record_length:
                    return _mid
                elif ts < look_for:
                    _low = _mid + 1
                else:
                    _high = _mid - 1

        return -1

    @property
    def _record_length(self) -> int:
        return self.data_series.record_length()

    @property
    def _header_length(self) -> int:
        return self.data_series.header_length()

    def _read_timestamp(self, f, offset):
        f.seek(offset)
        line = f.readline()
        return DataPoint.from_csv(line, self.data_series.csv_header()).timestamp


    def _align_to_record(self, _offset: int) -> int:
        _from_header = _offset - self._header_length
        _num_records = _from_header // self._record_length
        return self._header_length + (_num_records * self._record_length)
