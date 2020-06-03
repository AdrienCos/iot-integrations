from __future__ import division
from webthing import Thing
import logging
import config as cfg
import paho.mqtt.client as mqtt
import time


class SIISThing(Thing):
    "An abstract sensor on which all SIIS devices are based"

    def __init__(self, mqtt_name: str = "mqtt_abstract", uri: str = "urn:dev:siis:abstract", title: str = "Abstract Sensor", capabilities: list = [], desc: str = "An abstract device"):
        Thing.__init__(
            self,
            id_=uri,
            title=title,
            type_=capabilities,
            description=desc
        )
        self.name: str = mqtt_name
        self.scheduler_topic: str = cfg.scheduler_topic + self.name
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.tls_set(ca_certs=cfg.cafile,
                            certfile=cfg.certfile,
                            keyfile=cfg.keyfile)
        self.connect()

    def connect(self) -> None:
        self.client.connect(cfg.broker_addr, port=cfg.port)
        self.client.loop_start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        logging.debug("Connected to broker")
        self.client.subscribe(self.scheduler_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        raise NotImplementedError()
