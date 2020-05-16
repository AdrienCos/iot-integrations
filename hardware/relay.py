from gpiozero import DigitalOutputDevice
from time import sleep


class Relay():
    "Simple wrapper for a power relay"

    def __init__(self, pin: int):
        self.device = DigitalOutputDevice(pin)

    @property
    def value(self) -> bool:
        return bool(self.device.value)

    def set(self) -> None:
        self.device.on()

    def unset(self) -> None:
        self.device.off()

    def toggle(self) -> None:
        self.device.toggle()


if __name__ == "__main__":
    relay = Relay(25)
    while (True):
        relay.toggle()
        sleep(0.5)
