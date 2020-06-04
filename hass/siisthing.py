import paho.mqtt.client as mqtt

import config as cfg


class SIISThing():
    def __init__(self, name: str = "mqtt_abstract_1"):
        self.name: str = name
        self.auto_update: bool = True
        self.scheduler_topic: str = cfg.scheduler_topic + self.name
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.set_topic: str = cfg.base_topic + self.name + cfg.set_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix

        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.tls_set(ca_certs=cfg.cafile,
                            certfile=cfg.certfile,
                            keyfile=cfg.keyfile)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print(f"Connected to MQTT broker at {cfg.broker_addr}")
        self.client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        self.client.subscribe(self.set_topic)
        self.client.subscribe(self.scheduler_topic)

    def connect(self):
        self.client.connect(cfg.broker_addr, port=cfg.port)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError
