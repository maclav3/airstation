import time

# Timestamps returned by esp32 are in Embedded Epoch Time (seconds since 2000-01-01 00:00:00 UTC) as opposed to
# Unix/POSIX Epoch Time (seconds since 1970-01-01 00:00:00 UTC).
_epoch_offset = 946684800


class Timestamp:
    @staticmethod
    def from_embedded_epoch(timestamp: int) -> "Timestamp":
        return Timestamp(timestamp + _epoch_offset)

    @staticmethod
    def from_str(timestamp: str) -> "Timestamp":
        return Timestamp(int(timestamp))

    @staticmethod
    def from_unix_epoch(timestamp: int) -> "Timestamp":
        return Timestamp(timestamp)

    @staticmethod
    def now() -> "Timestamp":
        return Timestamp.from_embedded_epoch(time.time())

    def __init__(self, timestamp: int):
        self.timestamp: int = int(timestamp)

    def __int__(self) -> int:
        return self.timestamp

    def __str__(self) -> str:
        return str(self.timestamp)

    def __repr__(self) -> str:
        return str(self.timestamp)

    def __eq__(self, other: "Timestamp") -> bool:
        return isinstance(other, Timestamp) and self.timestamp == other.timestamp

    def __lt__(self, other: "Timestamp") -> bool:
        return self.timestamp < other.timestamp

    def __le__(self, other: "Timestamp") -> bool:
        return self.timestamp <= other.timestamp

    def __gt__(self, other: "Timestamp") -> bool:
        return self.timestamp > other.timestamp

    def __ge__(self, other: "Timestamp") -> bool:
        return self.timestamp >= other.timestamp

    def __add__(self, other: int or "Timestamp") -> "Timestamp":
        return Timestamp.from_unix_epoch(self.timestamp + int(other))

    def __sub__(self, other: int or "Timestamp") -> "Timestamp":
        return Timestamp.from_unix_epoch(self.timestamp - int(other))

    def __hash__(self) -> int:
        return hash(self.timestamp)


class DataColumn:
    def __init__(self, name: str, width: int, initializer, unit=''):
        self.name = name
        self.width = width
        self.initializer = initializer
        self.unit = unit

    def __str__(self):
        return f"{self.name} ({self.width})"


# Supported data columns
DATA_COLUMN_TIMESTAMP = DataColumn("timestamp", 10, Timestamp)  # unix timestamp
DATA_COLUMN_TEMPERATURE = DataColumn("temperature", 6, float, '\u00B0C')
DATA_COLUMN_PRESSURE = DataColumn("pressure", 7, float, 'hPa')
DATA_COLUMN_RELATIVE_HUMIDITY = DataColumn("relative_humidity", 5, float, '%')
DATA_COLUMN_AQI = DataColumn("aqi", 1, int)  # Air Quality Index
DATA_COLUMN_TVOC = DataColumn("tvoc", 4, int, 'ppb')  # Total Volatile Organic Compounds in ppb
DATA_COLUMN_ECO2 = DataColumn("eCO2", 4, int, 'ppm')  # Equivalent CO2 in ppm

supported_data_columns = [
    DATA_COLUMN_TIMESTAMP,
    DATA_COLUMN_TEMPERATURE,
    DATA_COLUMN_PRESSURE,
    DATA_COLUMN_RELATIVE_HUMIDITY,
    DATA_COLUMN_AQI,
    DATA_COLUMN_TVOC,
    DATA_COLUMN_ECO2,
]


class DataPoint:
    """DataPoint class represents a data point in a time series."""

    def __init__(self, **kwargs):
        self.columns: list[DataColumn] = []
        col_names = [col.name for col in supported_data_columns]

        for k, v in kwargs.items():
            if k not in col_names:
                raise ValueError(f"Unsupported column: {k}")
            data_column = next((dc for dc in supported_data_columns if dc.name == k), None)
            if not isinstance(v, data_column.initializer):
                raise ValueError(f"Invalid type for {k}: {type(v)}")
            setattr(self, k, v)
            self.columns.append(data_column)

        if not hasattr(self, "timestamp"):
            raise ValueError("Missing timestamp")

    def __str__(self) -> str:
        s = f"DataPoint({self.timestamp}"
        for column in supported_data_columns:
            if hasattr(self, column.name):
                s += f", {column.name}={getattr(self, column.name)} {column.unit}"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        _dict = {
            "timestamp": self.timestamp
        }

        for column in supported_data_columns:
            if hasattr(self, column.name):
                _dict[column.name] = getattr(self, column.name)

        return _dict

    @staticmethod
    def from_dict(data: dict) -> "DataPoint":
        return DataPoint(**data)

    def to_csv(self, columns: list[DataColumn] = None) -> str:
        # pad the timestamp to supported_data_columns["timestamp"].width
        _csv = str(self.timestamp).rjust(DATA_COLUMN_TIMESTAMP.width)

        for column in supported_data_columns:
            if column == DATA_COLUMN_TIMESTAMP:
                continue
            if columns and column not in columns:
                continue
            if hasattr(self, column.name):
                _value = str(getattr(self, column.name))
                _value = _value.rjust(column.width)
                _csv += f",{_value}"

        return _csv + "\n"

    @staticmethod
    def from_csv(data: str, header: str) -> "DataPoint":
        _columns = header.strip().split(",")
        _values = data.strip().split(",")

        _data = {}
        for i, column in enumerate(supported_data_columns):
            if not column.name in _columns:
                continue
            _data[column.name] = column.initializer(_values[i])

        return DataPoint(**_data)


class DataSeries:
    def __init__(self, columns: list[DataColumn], data: list[DataPoint]):
        self.columns = columns
        self.data = data

    def csv_header(self, columns: list[DataColumn] = None) -> str:
        _output_columns = self.columns
        if columns:
            _output_columns = columns

        return ','.join([column.name for column in _output_columns]) +  "\n"

    def header_length(self) -> int:
        return len(self.csv_header())

    def record_length(self) -> int:
        _length = 0
        for column in self.columns:
            _length += column.width + 1
        return _length + 1

    def with_columns(self, columns: list[DataColumn]) -> "DataSeries":
        return DataSeries(columns, self.data)

    def append(self, data: DataPoint):
        if not isinstance(data, DataPoint):
            raise ValueError("Invalid data type")
        if data.columns != self.columns:
            raise ValueError("Data columns do not match")
        self.data.append(data)

    def to_csv(self, columns: list[DataColumn] = None) -> str:
        if not columns:
            columns = self.columns

        _csv = self.csv_header(columns)
        for dp in self.data:
            _csv += dp.to_csv(columns)
        return _csv

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key: int) -> DataPoint:
        return self.data[key]
