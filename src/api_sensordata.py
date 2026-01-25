import urequests

_pm25norm = 25
_pm10norm = 50

class SensorData:
    def __init__(self, **kwargs):
        self.pm10: float | None = kwargs.get("pm10", None)
        self.pm25: float | None = kwargs.get("pm25", None)
        self.aqi: int | None = kwargs.get("aqi", None)

    def __str__(self) -> str:
        _pm10 = self.pm10 if self.pm10 is not None else 0
        _pm10Percent = "{:.2f}".format((_pm10 / _pm10norm * 100))

        _pm25 = self.pm25 if self.pm25 is not None else 0
        _pm25Percent = "{:.2f}".format((_pm25 / _pm25norm * 100))

        s = f"PM10: {self.pm10} ({_pm10Percent}%)\nPM2.5: {self.pm25} ({_pm25Percent}%)"
        if self.aqi is not None:
            s += f"\nAQI: {self.aqi}"

        return s

    "to_lcd renders the data as two rows that can be displayed on a 16x2 LCD"
    def to_lcd(self) -> tuple[str, str]:
        # P25|999ugm3|500%
        # P10|999ugm3|500%
        pm25percent = int(self.pm25 / _pm25norm * 100)
        p10percent = int(self.pm10 / _pm10norm * 100)

        pm25percent = "{:03d}".format(pm25percent) if pm25percent < 1000 else '!!!'
        p10percent = "{:03d}".format(p10percent) if p10percent < 1000 else '!!!'

        p25 = "P25|{:03d}ugm3|{}%".format(int(self.pm25), pm25percent)
        p10 = "P10|{:03d}ugm3|{}%".format(int(self.pm10), p10percent)
        return p25, p10


class SensorStation:
    def __init__(self, name: str, id: int, type: str):
        self.name = name
        self.id = id
        self.type = type

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


def get_sensor_community_data(station: SensorStation) -> SensorData:
    print("Getting sensor community data from station %s" % station)
    response = urequests.get(
        f"https://data.sensor.community/airrohr/v1/sensor/{station.id}/"
    )

    if response.status_code != 200:
        raise Exception(
            "Failed to get sensor community data; status code %d" % response.status_code
        )

    resp = response.json()
    try:
        last_measurements = resp[0]["sensordatavalues"]
    except IndexError or KeyError:
        print("Unexpected response from sensor.community API: %s" % resp)
        return SensorData()

    sd = SensorData()
    for m in last_measurements:
        if m["value_type"] == "P1":
            sd.pm10 = float(m["value"])
        if m["value_type"] == "P2":
            sd.pm25 = float(m["value"])

    return sd