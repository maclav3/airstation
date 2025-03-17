import unittest

from measurements import DataPoint, Timestamp, DATA_COLUMN_TIMESTAMP, DATA_COLUMN_TEMPERATURE, DATA_COLUMN_ECO2


class TestDataPoint(unittest.TestCase):
    def test_data_point(self):
        dp = DataPoint(
            timestamp=Timestamp(100),
            temperature=1.0,
            pressure=1.0,
            relative_humidity=1.0,
            aqi=1,
            tvoc=1,
            eCO2=1,
        )
        self.assertEqual(Timestamp(100), dp.timestamp)
        self.assertEqual(1.0, dp.temperature)
        self.assertEqual(1.0, dp.pressure)
        self.assertEqual(1.0, dp.relative_humidity)
        self.assertEqual(1.0, dp.aqi)
        self.assertEqual(1.0, dp.tvoc)
        self.assertEqual(1.0, dp.eCO2)

    def test_data_point_to_csv(self):
        dp = DataPoint(
            timestamp=Timestamp(100),
            temperature=200.0,
            pressure=300.0,
            relative_humidity=40.0,
            aqi=5,
            tvoc=6,
            eCO2=7,
        )
        self.assertEqual('       100, 200.0,  300.0, 40.0,5,   6,   7\n', dp.to_csv())

    def test_data_point_to_csv_column_subset(self):
        dp = DataPoint(
            timestamp=Timestamp(100),
            temperature=2.0,
            pressure=3.0,
            relative_humidity=4.0,
            aqi=5,
            tvoc=6,
            eCO2=7,
        )
        self.assertEqual(dp.to_csv({DATA_COLUMN_TIMESTAMP, DATA_COLUMN_ECO2}), '       100,   7\n')

    def test_data_point_from_csv(self):
        dp = DataPoint.from_csv('123,456,1,2,3,4,5\n',
                                'timestamp,temperature,pressure,relative_humidity,aqi,tvoc,eCO2\n')
        self.assertEqual(dp.timestamp, Timestamp(123))
        self.assertEqual(dp.temperature, 456)
        self.assertEqual(dp.pressure, 1.0)
        self.assertEqual(dp.relative_humidity, 2.0)
        self.assertEqual(dp.aqi, 3)
        self.assertEqual(dp.tvoc, 4)
        self.assertEqual(dp.eCO2, 5)
