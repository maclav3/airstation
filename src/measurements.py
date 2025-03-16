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
        self.timestamp: int = kwargs.get("timestamp")
        self.temperature: float | None = kwargs.get("temperature")
        self.pressure: float = kwargs.get("pressure")
        self.relative_humidity = kwargs.get("relative_humidity")
        self.aqi = kwargs.get("aqi")
        self.tvoc = kwargs.get("tvoc")
        self.eCO2 = kwargs.get("eCO2")

    def __str__(self) -> str:
        return f"{self.timestamp}: T={self.temperature}°C, P={self.pressure}hPa, RH={self.relative_humidity}%, AQI={self.aqi}, TVOC={self.tvoc}ppb, eCO2={self.eCO2}ppm"

    def __repr__(self) -> str:
        return self.__str__()

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
        return f"{self.timestamp},{self.temperature},{self.pressure},{self.relative_humidity},{self.aqi},{self.tvoc},{self.eCO2}"

    @staticmethod
    def from_csv(data: str) -> "DataPoint":
        timestamp, temperature, pressure, relative_humidity, aqi, tvoc, eCO2 = data.split(",")
        return DataPoint(
            timestamp=timestamp,
            temperature=temperature,
            pressure=pressure,
            relative_humidity=relative_humidity,
            aqi=aqi,
            tvoc=tvoc,
            eCO2=eCO2,
        )

    @staticmethod
    def csv_header() -> str:
        return "timestamp,temperature,pressure,relative_humidity,aqi,tvoc,eCO2"

