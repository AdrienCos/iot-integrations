# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading
import config as cfg

from hardware.barometer import Barometer
from hardware.thermometer import Thermometer


class SIISSensor():
    def __init__(self, name: str = "mqtt_sensor_1"):
        self.name: str = name
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.temp_state_topic: str = cfg.base_topic + self.name + "/thermometer" + cfg.state_suffix
        self.humidity_state_topic: str = cfg.base_topic + self.name + "/hygrometer" + cfg.state_suffix
        self.pressure_state_topic: str = cfg.base_topic + self.name + "/barometer" + cfg.state_suffix
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(cfg.username, cfg.password)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

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
        print("Connected to MQTT server at %s" % (cfg.broker_addr))
        client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        client.publish(self.temp_state_topic, payload=self.get_temp(), qos=1, retain=True)
        client.publish(self.humidity_state_topic, payload=self.get_humidity(), qos=1, retain=True)
        client.publish(self.pressure_state_topic, payload=self.get_pressure(), qos=1, retain=True)

    def connect(self, addr: str = cfg.broker_addr) -> None:
        self.client.connect(addr, port=cfg.port)

    def start(self):
        self.connect()
        self.client.loop_start()
        self.start_polling()


# Start polling the files
if __name__ == "__main__":
    sensor = SIISSensor()
    sensor.start()
