import os
import unittest
from tempfile import mktemp
from measurements import Timestamp
from measurements import DataPoint
from db import DB


class MyTestCase(unittest.TestCase):
    db_file = mktemp(".csv")
    db = DB(db_file)

    _start = 1000
    _start_timestamp = Timestamp(_start)
    _end = _start + 2000
    _end_timestamp = Timestamp(_end)
    _time_step = 10

    _num_records = (_end - _start) // _time_step

    def test_insert(self):
        for i, t in enumerate(range(int(self._start_timestamp), int(self._end_timestamp), self._time_step)):
            timestamp = Timestamp.from_unix_epoch(t)
            i = i % 100
            self.db.insert(DataPoint(timestamp=timestamp, temperature=i, pressure=i, relative_humidity=i, aqi=1, tvoc=i, eCO2=i))
        self.assertTrue(os.path.exists(self.db_file))

    def test_read_all(self):
        data = self.db.read(None, None)
        self.assertEqual(len(data), self._num_records)
        self.assertEqual(data[0].timestamp, self._start_timestamp)
        self.assertEqual(data[-1].timestamp, self._end_timestamp - self._time_step)

    def test_read_with_maximum_bounds(self):
        data = self.db.read(self._start_timestamp, self._end_timestamp)
        self.assertEqual(len(data), self._num_records)
        self.assertEqual(data[0].timestamp, self._start_timestamp)
        self.assertEqual(data[-1].timestamp, self._end_timestamp - self._time_step)

    def test_read_with_bounds_more_than_maximum(self):
        data = self.db.read(self._start_timestamp - 1000, self._end_timestamp + 1000)
        self.assertEqual(len(data), self._num_records)
        self.assertEqual(data[0].timestamp, self._start_timestamp)
        self.assertEqual(data[-1].timestamp, self._end_timestamp - self._time_step)

    def test_read_with_min_bound(self):
        data = self.db.read(self._start_timestamp + 10 * self._time_step, None)
        self.assertEqual(len(data), self._num_records - 10)
        self.assertEqual(data[0].timestamp, self._start_timestamp + 10 * self._time_step)
        self.assertEqual(data[-1].timestamp, self._end_timestamp - self._time_step)

    def test_read_with_max_bound(self):
        data = self.db.read(None, self._end_timestamp - 10 * self._time_step)
        self.assertEqual(len(data), self._num_records - 10)
        self.assertEqual(data[0].timestamp, self._start_timestamp)
        self.assertEqual(data[-1].timestamp, self._end_timestamp - 10 * self._time_step - self._time_step)

    def test_read_with_bounds(self):
        data = self.db.read(
            self._start_timestamp + 10 * self._time_step, self._end_timestamp - 10 * self._time_step
        )
        self.assertEqual(len(data), self._num_records - 20)
        self.assertEqual(data[0].timestamp, self._start_timestamp + 10 * self._time_step)
        self.assertEqual(data[-1].timestamp, self._end_timestamp - 10 * self._time_step - self._time_step)

    def test_with_bound_between_records(self):
        data = self.db.read(None, self._start_timestamp + 105)
        # should work just like 100 – the records are spaced 10 seconds apart
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0].timestamp, self._start_timestamp)
        self.assertEqual(data[-1].timestamp, self._start_timestamp + 100 - self._time_step)


if __name__ == "__main__":
    unittest.main()
