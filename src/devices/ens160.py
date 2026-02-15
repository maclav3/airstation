from lib.ens160 import ENS160


class ENS160_calibrated(ENS160):
    def __init__(self, i2c, address=0x53):
        super().__init__(i2c, address)

    def set_ambient_temp(self, value_in_celsius: float):
        """write ambient temperature data to ENS160 for compensation. value in Celsius.
        This value must be read from the temperature sensor! It must be correct!
        """
        t = int(64 * (273.15 + value_in_celsius))
        _v = t.to_bytes(2)
        self._write_register(0x13, _v)

    def set_humidity(self, rel_hum: float):
        """write relative humidity data to ENS160 for compensation. value in percent."""
        _rel_hum = int(rel_hum)
        if _rel_hum not in range(101):
            raise ValueError(f"Invalid humidity value: {rel_hum}")
        _v = (_rel_hum << 9).to_bytes(2)
        self._write_register(0x15, _v)
