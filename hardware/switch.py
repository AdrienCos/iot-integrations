from gpiozero import Button

from time import sleep


class Switch():
    def __init__(self, pin: int):
        self.device = Button(pin)

    @property
    def value(self) -> bool:
        value = self.device.is_pressed
        return value


if __name__ == "__main__":
    button = Switch(18)

    while True:
        print(button.value)
        sleep(0.5)
