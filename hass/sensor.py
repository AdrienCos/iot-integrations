# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading
import config as cfg


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

    @staticmethod
    def get_temp() -> str:
        # Replace code here with actual device querying
        return "%0.1f" % (random.random() * 20 + 10)

    @staticmethod
    def get_humidity() -> str:
        # Replace code here with actual device querying
        return "%0.1f" % (random.random() * 100)

    @staticmethod
    def get_pressure() -> str:
        # Replace code here with actual device querying
        return "%0.1f" % (random.random() * 6 + 1015.25)

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
