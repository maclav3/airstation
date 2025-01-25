import requests, toml

_pm25norm = 25
_pm10norm = 50

class SensorData:
    def __init__(self):
        self.pm10: float = None
        self.pm25: float = None

    def __str__(self):
        _pm10 = self.pm10 if self.pm10 is not None else 0
        _pm10Percent = "{:.2f}".format((_pm10/_pm10norm * 100))

        _pm25 = self.pm25 if self.pm25 is not None else 0
        _pm25Percent = "{:.2f}".format((_pm25/_pm25norm * 100))

        return f"PM10: {self.pm10} ({_pm10Percent}%)\nPM2.5: {self.pm25} ({_pm25Percent}%)"

class SensorStation:
    def __init__(self, name: str, id: int, type: str):
        self.name = name
        self.id = id
        self.type = type

    def __str__(self):
        return f"{self.name} ({self.id})"

def get_sensor_community_data(station: SensorStation) -> SensorData:
    print("Getting sensor community data from station %s" % station)
    response = requests.get(f"https://data.sensor.community/airrohr/v1/sensor/{station.id}/")

    if response.status_code != 200:
        raise Exception("Failed to get sensor community data; status code %d" % response.status_code)

    resp = response.json()
    last_measurements = resp[0]['sensordatavalues']

    sd = SensorData()
    for m in last_measurements:
        if m['value_type'] == 'P1':
            sd.pm10 = float(m['value'])
        if m['value_type'] == 'P2':
            sd.pm25 = float(m['value'])

    return sd

if __name__ == '__main__':
    toml_data = toml.load("config.toml")

    for line in toml_data['stations']:
        station = SensorStation(line['name'], line['id'], line['type'])
        if station.type == 'sensor.community':
            data = get_sensor_community_data(station)
            print(data)