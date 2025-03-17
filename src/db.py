from measurements import DataPoint, Timestamp
import os


class DB:
    def __init__(self, path: str):
        self._path = path

        try:
            os.stat(path)
        except OSError:
            # create file if it does not exist
            with open(path, "w") as f:
                f.write(DataPoint.CSV_HEADER)

    def insert(self, data: DataPoint):
        with open(self._path, "a") as f:
            f.write(data.to_csv())

    def read(self, _from: Timestamp = None, _to: Timestamp = None) -> list[DataPoint]:
        """read data points from the database between the given timestamps"""

        if _from is None:
            _from_offset = DataPoint.HEADER_LENGTH + 1
        else:
            _from_offset = self._find_timestamp_offset(_from)

        if _to is None:
            _to_offset = self._file_size()
        else:
            _to_offset = self._find_timestamp_offset(_to)

        if _from_offset == -1 or _to_offset == -1:
            return []

        with open(self._path, "r") as f:
            f.seek(_from_offset)
            data = []
            while f.tell() < _to_offset and f.tell() < self._file_size():
                _line = f.readline()
                dp = DataPoint.from_csv(_line)
                data.append(dp)

        return data

    def _file_size(self) -> int:
        return os.stat(self._path).st_size

    def _find_timestamp_offset(self, look_for: Timestamp) -> int:
        """find the offset of the line with the given timestamp using binary search"""
        _low = DataPoint.HEADER_LENGTH
        _high = self._file_size()

        with open(self._path, "r") as f:
            _last = self._read_timestamp(f, _high - DataPoint.RECORD_LENGTH)
            if look_for >= _last:
                return _high

            _first = self._read_timestamp(f, DataPoint.HEADER_LENGTH)
            if look_for <= _first:
                return DataPoint.HEADER_LENGTH

            # rewind to first record
            f.seek(DataPoint.HEADER_LENGTH)

            while _low < _high:
                _mid = (_low + _high) // 2
                _mid = _align_to_record(_mid)

                ts = self._read_timestamp(f, _mid)
                if ts == look_for or _high - _low < DataPoint.RECORD_LENGTH:
                    return _mid
                elif ts < look_for:
                    _low = _mid + 1
                else:
                    _high = _mid - 1

        return -1

    @staticmethod
    def _read_timestamp(f, offset):
        f.seek(offset)
        line = f.readline()
        return DataPoint.from_csv(line).timestamp


def _align_to_record(_offset: int) -> int:
    _from_header = _offset - DataPoint.HEADER_LENGTH
    _num_records = _from_header // DataPoint.RECORD_LENGTH
    return DataPoint.HEADER_LENGTH + (_num_records * DataPoint.RECORD_LENGTH)
