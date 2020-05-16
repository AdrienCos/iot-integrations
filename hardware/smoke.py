from gpiozero import DigitalInputDevice
from typing import Callable
from time import sleep


class SmokeDetector():
    "Simple wrapper for a smoke detector device"

    def __init__(self, pin: int, activated: Callable, deactivated: Callable):
        self.sensor = DigitalInputDevice(pin, pull_up=None, active_state=False)
        self.sensor.when_activated = activated
        self.sensor.when_deactivated = deactivated

    @property
    def value(self) -> bool:
        return bool(self.sensor.value)


if __name__ == "__main__":
    def alarm_on():
        print("Alarm On")

    def alarm_off():
        print("Alarm Off")
    smoke = SmokeDetector(25, alarm_on, alarm_off)

    while (True):
        sleep(1)
