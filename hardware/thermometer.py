from bmp280 import BMP280
from smbus2 import SMBus
from time import sleep


class Thermometer():
    def __init__(self, addr=0x77):
        "Simple I2C thermometer"
        self.bus = SMBus(1)
        self.device = BMP280(i2c_dev=self.bus, i2c_addr=addr)

    @property
    def value(self) -> float:
        "Temperature in C"
        temp = self.device.get_temperature()
        return temp


if __name__ == "__main__":
    thermo = Thermometer()
    while True:
        print(thermo.value)
        sleep(0.5)
