# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading
import config as cfg

from siisthing import SIISThing

from hardware.barometer import Barometer
from hardware.thermometer import Thermometer


class SIISSensor(SIISThing):
    def __init__(self, name: str = "sensor_1"):
        SIISThing.__init__(self, name)
        self.temp_state_topic: str = cfg.base_topic + self.name + "/thermometer" + cfg.state_suffix
        self.humidity_state_topic: str = cfg.base_topic + self.name + "/hygrometer" + cfg.state_suffix
        self.pressure_state_topic: str = cfg.base_topic + self.name + "/barometer" + cfg.state_suffix

        self.thermometer = Thermometer()
        self.barometer = Barometer()
        self.hygrometer = Barometer()

    def get_temp(self) -> str:
        # Replace code here with actual device querying
        temp = self.thermometer.value
        return "%0.1f" % (temp)

    def get_humidity(self) -> str:
        # Replace code here with actual device querying
        _ = self.hygrometer.value
        return "%0.1f" % (random.random() * 100)

    def get_pressure(self) -> str:
        # Replace code here with actual device querying
        press = self.barometer.value
        return "%0.1f" % (press)

    def start_polling(self) -> None:
        self.client.publish(self.temp_state_topic, payload=self.get_temp(), qos=1, retain=True)
        self.client.publish(self.humidity_state_topic, payload=self.get_humidity(), qos=1, retain=True)
        self.client.publish(self.pressure_state_topic, payload=self.get_pressure(), qos=1, retain=True)
        threading.Timer(cfg.update_delay, self.start_polling).start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        SIISThing.on_connect(self, client, userdata, flags, rc)
        client.publish(self.temp_state_topic, payload=self.get_temp(), qos=1, retain=True)
        client.publish(self.humidity_state_topic, payload=self.get_humidity(), qos=1, retain=True)
        client.publish(self.pressure_state_topic, payload=self.get_pressure(), qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            print(f"Received an unexpected message from the scheduler: {message.payload.decode()}")
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def start(self):
        self.connect()
        self.client.loop_start()
        self.start_polling()


# Start polling the files
if __name__ == "__main__":
    sensor = SIISSensor()
    sensor.start()
