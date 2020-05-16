from gpiozero import MotionSensor
from typing import Callable
from time import sleep


class PIR():
    "Simple wrapper for a PIR device "

    def __init__(self, pin: int, activated: Callable, deactivated: Callable):
        self.sensor = MotionSensor(pin, sample_rate=10, queue_len=1)
        self.sensor.when_motion = activated
        self.sensor.when_no_motion = deactivated

    @property
    def value(self) -> bool:
        return self.sensor.motion_detected


if __name__ == "__main__":
    def motion():
        print("Motion")

    def no_motion():
        print("No Motion")
    pir = PIR(25, motion, no_motion)

    while (True):
        print(pir.value)
        sleep(1)
