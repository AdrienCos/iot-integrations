# from config_node import *
import paho.mqtt.client as mqtt
import threading
import config as cfg

from hardware.smoke import SmokeDetector


class SIISSmoke():
    def __init__(self, name: str = "mqtt_smoke_1"):
        self.name = name
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.tls_set(ca_certs=cfg.cafile,
                            certfile=cfg.certfile,
                            keyfile=cfg.keyfile)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

        self.device: SmokeDetector = SmokeDetector(cfg.pin, self.activated, self.deactivated)

    def get_state(self) -> str:
        # Replace code here with actual device querying
        state: bool = self.device.value
        if state:
            return "ON"
        return "OFF"

    def activated(self) -> None:
        pass

    def deactivated(self) -> None:
        pass

    def start_polling(self) -> None:
        self.client.publish(self.state_topic, payload=self.get_state(), qos=1, retain=True)
        threading.Timer(cfg.update_delay, self.start_polling).start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        client.publish(self.state_topic, payload=self.get_state(), qos=1, retain=True)

    def connect(self, addr: str = cfg.broker_addr) -> mqtt.Client:
        self.addr: str = addr
        self.client.connect(self.addr, port=cfg.port)

    def start(self):
        self.connect()
        self.client.loop_start()
        self.start_polling()


# Start polling the files
if __name__ == "__main__":
    smoke = SIISSmoke()
    smoke.start()
