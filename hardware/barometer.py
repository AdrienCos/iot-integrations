from bmp280 import BMP280
from smbus2 import SMBus
from time import sleep


class Barometer():
    def __init__(self, addr=0x77):
        "Simple I2C barometer handler"
        self.bus = SMBus(1)
        self.device = BMP280(i2c_dev=self.bus, i2c_addr=addr)

    @property
    def value(self) -> float:
        "Atmospheric pressure in hPa"
        temp = self.device.get_pressure()
        return temp


if __name__ == "__main__":
    thermo = Barometer()
    while True:
        print(thermo.value)
        sleep(0.5)
