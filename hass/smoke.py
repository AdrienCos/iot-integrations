# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading
import config as cfg


class SIISSmoke():
    def __init__(self, name: str = "mqtt_smoke_1"):
        self.name = name
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(cfg.username, cfg.password)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

    def get_state(self) -> str:
        # Replace code here with actual device querying
        return "ON" if random.random() > 0.7 else "OFF"

    def start_polling(self) -> None:
        self.client.publish(self.state_topic, payload=self.get_state(), qos=1, retain=True)
        threading.Timer(cfg.update_delay, self.start_polling).start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        client.publish(self.available_topic, payload="online", qos=1, retain=True)
        client.publish(self.state_topic, payload=self.get_state(), qos=1, retain=True)

    def connect(self, addr: str = cfg.broker_addr) -> mqtt.Client:
        self.addr: str = addr
        self.client.connect(self.addr, port=cfg.port)


# Start polling the files
if __name__ == "__main__":
    smoke = SIISSmoke()
    smoke.connect()
    smoke.client.loop_start()
    smoke.start_polling()
