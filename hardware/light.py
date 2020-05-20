from rpi_ws281x import PixelStrip
from time import sleep
from typing import Tuple
from kelvin import kelvin_table


MODE_RGB = 0
MODE_TEMPERATURE = 1


class RGBLight():
    "Simple wrapper for a RGB light device "

    def __init__(self, pin: int, nb_led: int = 5):
        self.pixels = PixelStrip(nb_led, pin)
        self.pixels.begin()
        self._state: bool = False
        self.delay: float = 0.01
        self._mode: int = MODE_RGB

        self.off()

    @property
    def state(self) -> bool:
        return self._state

    @state.setter
    def state(self, state: bool) -> None:
        self._state = state

    @property
    def mode(self) -> int:
        return self._mode

    @mode.setter
    def mode(self, mode) -> None:
        self._mode = mode

    def on(self) -> None:
        self.state = True
        for i in range(self.pixels.numPixels()):
            print(i)
            self.pixels.setPixelColorRGB(i, 50, 50, 50)
            self.pixels.show()
            sleep(0.01)

    def off(self) -> None:
        self.state = False
        for i in range(self.pixels.numPixels()):
            self.pixels.setPixelColorRGB(i, 0, 0, 0)
            self.pixels.show()
            sleep(self.delay)

    def toggle(self) -> None:
        if self.state is True:
            self.off()
        else:
            self.on()

    @property
    def color(self) -> Tuple[int, int, int]:
        if self.mode != MODE_RGB:
            raise Exception("Light is not in RGB mode")
        color_raw = self.pixels.getPixelColorRGB(0)
        color = (color_raw.r, color_raw.g, color_raw.b)
        return color

    @color.setter
    def color(self, color: Tuple[int, int, int]) -> None:
        self.state = True
        self.mode = MODE_RGB
        for i in range(self.pixels.numPixels()):
            self.pixels.setPixelColorRGB(i, *color)
            self.pixels.show()
            sleep(self.delay)

    @property
    def brightness(self) -> int:
        bri = self.pixels.getBrightness()
        return bri

    @brightness.setter
    def brightness(self, value: int) -> None:
        self.pixels.setBrightness(value)

    @property
    def temperature(self) -> int:
        if self.mode != MODE_TEMPERATURE:
            raise Exception("Light is not in temperature mode")
        color_raw = self.pixels.getPixelColorRGB(0)
        rgb = (color_raw.r, color_raw.g, color_raw.b)
        print(rgb)
        for temp in kelvin_table.keys():
            if kelvin_table[temp] == rgb:
                return temp

        return 0

    @temperature.setter
    def temperature(self, temp: int) -> None:
        self.mode = MODE_TEMPERATURE
        safe_temp = temp - (temp % 100)
        rgb: Tuple[int, int, int] = kelvin_table[safe_temp]
        for i in range(self.pixels.numPixels()):
            self.pixels.setPixelColorRGB(i, *rgb)
            self.pixels.show()
            sleep(self.delay)


if __name__ == "__main__":
    light = RGBLight(18)

    while (True):
        temp1 = 1800
        temp2 = 5000
        temp3 = 1330
        light.temperature = temp1
        sleep(0.5)
        light.temperature = temp2
        sleep(0.5)
        light.temperature = temp3
        sleep(0.5)

        rgb1 = (0, 10, 100)
        rgb2 = (200, 20, 50)
        light.color = rgb1
        sleep(0.5)
        light.color = rgb2
        sleep(0.5)
        light.off()
        sleep(0.5)
