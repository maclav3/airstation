import requests
import json
import time

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


class SensorStation:
    def __init__(self, name: str, id: int, type: str):
        self.name = name
        self.id = id
        self.type = type

    def __str__(self) -> str:
        return f"{self.name} ({self.id})"


def get_sensor_community_data(station: SensorStation) -> SensorData:
    print("Getting sensor community data from station %s" % station)
    response = requests.get(
        f"https://data.sensor.community/airrohr/v1/sensor/{station.id}/"
    )

    if response.status_code != 200:
        raise Exception(
            "Failed to get sensor community data; status code %d" % response.status_code
        )

    resp = response.json()
    last_measurements = resp[0]["sensordatavalues"]

    sd = SensorData()
    for m in last_measurements:
        if m["value_type"] == "P1":
            sd.pm10 = float(m["value"])
        if m["value_type"] == "P2":
            sd.pm25 = float(m["value"])

    return sd


def get_pms7003_data() -> SensorData:
    print("Getting data from a local PMS7003 sensor")
    from src.devices.pms7003 import Pms7003
    from src.devices.aqi import AQI

    pms = Pms7003(2)
    pms_data = pms.read()
    aqi = AQI.aqi(pms_data["PM2_5_ATM"], pms_data["PM10_0_ATM"])

    return SensorData(pm10=pms_data["PM10_0_ATM"], pm25=pms_data["PM2_5_ATM"], aqi=aqi)


if __name__ == "__main__":
    with open("../config.json") as f:
        _conf = json.load(f)

    for _entry in _conf["stations"]:
        station = SensorStation(_entry["name"], _entry["id"], _entry["type"])
        if station.type == "sensor.community":
            data = get_sensor_community_data(station)
            print(data)

    while True:
        print(get_pms7003_data())
        time.sleep(10)
