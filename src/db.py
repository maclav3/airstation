from measurements import DataPoint
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

    def read(
        self, from_timestamp: int | None, to_timestamp: int | None
    ) -> list[DataPoint]:
        """read data points from the database between the given timestamps"""

        if from_timestamp is None:
            _from_offset = DataPoint.HEADER_LENGTH + 1
        else:
            _from_offset = self._find_timestamp_offset(from_timestamp)

        if to_timestamp is None:
            _to_offset = self._file_size()
        else:
            _to_offset = self._find_timestamp_offset(to_timestamp)

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

    def _find_timestamp_offset(self, timestamp: int) -> int:
        """find the offset of the line with the given timestamp using binary search"""
        _low = DataPoint.HEADER_LENGTH
        _high = self._file_size()

        with open(self._path, "r") as f:
            while _low < _high:
                _mid = (_low + _high) // 2
                _mid = _align_to_record(_mid)
                f.seek(_mid)

                _line = f.readline()
                dp = DataPoint.from_csv(_line)
                if dp.timestamp == timestamp or _high - _low < DataPoint.RECORD_LENGTH:
                    return _mid + DataPoint.RECORD_LENGTH
                elif dp.timestamp < timestamp:
                    _low = _mid + 1
                else:
                    _high = _mid - 1

        return -1


def _align_to_record(_offset: int) -> int:
    _from_header = _offset - DataPoint.HEADER_LENGTH
    _num_records = _from_header // DataPoint.RECORD_LENGTH
    return DataPoint.HEADER_LENGTH + (_num_records * DataPoint.RECORD_LENGTH)
