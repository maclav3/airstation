import time
import urequests
import json

from db import DB
from devices.ens160 import ENS160_calibrated
from machine import SoftI2C, Pin
from lib.BME280 import BME280, BME280_OSAMPLE_2
from measurements import DataPoint

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


def get_pms7003_data() -> SensorData:
    print("Getting data from a local PMS7003 sensor")
    from devices.pms7003 import Pms7003
    from devices.aqi import AQI

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

    from lib.microWebSrv import MicroWebSrv
    import server

    # import for routing side effect
    _ = server

    i2c = SoftI2C(scl=Pin(4), sda=Pin(16))

    # TODO: need to panic if the sensor is not connected
    ens160 = ENS160_calibrated(i2c)
    bme280 = BME280(mode=BME280_OSAMPLE_2, i2c=i2c)

    mws = MicroWebSrv(webPath="/www")  # TCP port 80 and files in /www
    mws.Start(threaded=True)  # Starts server in a new thread

    db = DB("/sd/data.csv")

    while True:
        _temp, _pres, _hum = 0., 0., 0.
        try:
            temp, pressure, hum = bme280.temperature, bme280.pressure, bme280.humidity
        except OSError as e:
            print("Failed to read BME280 data: %s" % e)
            temp, pressure, hum = None, None, None

        if temp and hum:
            _temp: float = float(temp[:-1])
            _pres: float = float(pressure[:-3])
            _hum = float(hum[:-1])

            ens160.set_ambient_temp(_temp)
            ens160.set_humidity(_hum)

            print(
                f"BME280Temp: {temp}\u00b0C\n"
                f"BME280Pressure: {pressure}\n"
                f"BME280RH: {hum}%\n"
            )

        aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating = ens160.read_air_quality()
        print(
            f"ENS160Temp: {temp:.1f}\u00b0C\n"
            f"ENS160RH: {rh:.1f}%\n"
            f"TVOC: {tvoc}\n"
            f"TVOC Rating: {tvoc_rating}\n"
            f"eCO2: {eco2}\n"
            f"eCO2 Rating: {eco2_rating}\n"
            f"AQI: {aqi}\n\n"
        )

        datapoint = DataPoint(
            timestamp=int(time.time()),
            temperature=_temp,
            pressure=_pres,
            relative_humidity=_hum,
            aqi=int(aqi),
            tvoc=int(tvoc),
            eCO2=int(eco2),
        )

        db.insert(datapoint)

        time.sleep(30)
