from gpiozero import Servo
from time import sleep


class ServoMotor():
    "Simple wrapper for a servomotor"

    def __init__(self, pin: int, min: int = 0, max: int = 180):
        self.device = Servo(pin)

    @property
    def state(self) -> bool:
        if self.device.value == -1:
            return False
        return True

    def on(self) -> None:
        self.device.max()

    def off(self) -> None:
        self.device.min()

    def toggle(self) -> None:
        if self.state is True:
            self.off()
        else:
            self.on()


if __name__ == "__main__":
    servo = ServoMotor(25)

    while True:
        servo.toggle()
        print(servo.state)
        sleep(0.5)
