import paho.mqtt.client as mqtt

import config as cfg

from intruder_node import IntruderNode


class SIISThing():
    def __init__(self, name: str = "mqtt_abstract_1"):
        # Variables
        self.name: str = name
        self.auto_update: bool = True
        self.scheduler_topic: str = cfg.scheduler_topic + self.name
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.set_topic: str = cfg.base_topic + self.name + cfg.set_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix

        # MQTT client
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log
        self.client.tls_set(ca_certs=cfg.cafile,
                            certfile=cfg.certfile,
                            keyfile=cfg.keyfile)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

        # Intruder modules
        self.intruder: IntruderNode = IntruderNode(self.name, self.client)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print(f"Connected to MQTT broker at {cfg.broker_addr}")
        self.client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        self.client.subscribe(self.set_topic)
        self.client.subscribe(self.scheduler_topic)
        self.intruder.on_connect(client, userdata, flags, rc)

    def connect(self):
        self.client.connect(cfg.broker_addr, port=cfg.port)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Pass the message down
        self.intruder.on_message(client, userdata, message)

    def on_log(self, client, userdata, level, buf):
        print("Log: %s" % (buf))
        pass

    def start(self) -> None:
        raise NotImplementedError


if __name__ == "__main__":
    thing = SIISThing()
    thing.connect()
    thing.client.loop_forever()
