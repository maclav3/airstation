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
        self.timestamp: int = timestamp

    def __int__(self) -> int:
        return self.timestamp

    def __str__(self) -> str:
        t = time.localtime(self.timestamp)
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6])

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: "Timestamp") -> bool:
        return self.timestamp == other.timestamp

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


class DataPoint:
    """DataPoint class represents a data point in a time series.
    Variables described by DataPoint are:
    - timestamp: int # unix timestamp
    - temperature: float # degrees Celsius
    - pressure: float # hPa
    - relative_humidity: float # percent
    - aqi: int # Air Quality Index
    - tvoc: int # Total Volatile Organic Compounds in ppb
    - eCO2: int # Equivalent CO2 in ppm

    The source for temperature, pressure, and relative humidity is BME280.
    The source for aqi, tvoc, and eCO2 is ENS160."""

    def __init__(self, **kwargs):
        self.timestamp: Timestamp = kwargs.get("timestamp")
        self.temperature: float = kwargs.get("temperature")
        self.pressure: float = kwargs.get("pressure")
        self.relative_humidity: float = kwargs.get("relative_humidity")
        self.aqi: int = kwargs.get("aqi")
        self.tvoc: int = kwargs.get("tvoc")
        self.eCO2: int = kwargs.get("eCO2")

    def __str__(self) -> str:
        return f"{self.timestamp}: T={self.temperature}°C, P={self.pressure}hPa, RH={self.relative_humidity}%, AQI={self.aqi}, TVOC={self.tvoc}ppb, eCO2={self.eCO2}ppm"

    def __repr__(self) -> str:
        return self.__str__()

    CSV_HEADER: str = "timestamp,temperature,pressure,relative_humidity,aqi,tvoc,eCO2\n"
    HEADER_LENGTH: int = len(CSV_HEADER)
    RECORD_LENGTH: int = len("1742195260,-12.34,1234.56,12.34,1,1234,1234\n")

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "relative_humidity": self.relative_humidity,
            "aqi": self.aqi,
            "tvoc": self.tvoc,
            "eCO2": self.eCO2,
        }

    @staticmethod
    def from_dict(data: dict) -> "DataPoint":
        return DataPoint(
            timestamp=data["timestamp"],
            temperature=data["temperature"],
            pressure=data["pressure"],
            relative_humidity=data["relative_humidity"],
            aqi=data["aqi"],
            tvoc=data["tvoc"],
            eCO2=data["eCO2"],
        )

    def to_csv(self) -> str:
        # make sure the csv has a constant width in bytes
        return f"{int(self.timestamp):10d},{self.temperature:-6.2f},{self.pressure:7.2f},{self.relative_humidity:5.2f},{self.aqi:1d},{self.tvoc:4d},{self.eCO2:4d}\n"

    @staticmethod
    def from_csv(data: str) -> "DataPoint":
        timestamp, temperature, pressure, relative_humidity, aqi, tvoc, eCO2 = (
            data.split(",")
        )
        return DataPoint(
            timestamp=Timestamp.from_str(timestamp),
            temperature=float(temperature),
            pressure=float(pressure),
            relative_humidity=float(relative_humidity),
            aqi=int(aqi),
            tvoc=int(tvoc),
            eCO2=int(eCO2),
        )
