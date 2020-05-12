# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg


class SIISPresence():
    def __init__(self, name: str = "mqtt_binary_1"):
        self.name: str = name
        self.last_state: str = "OFF"
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix
        self.scheduler_topic: str = cfg.scheduler_topic + self.name
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(cfg.username, cfg.password)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            tv_state = message.payload.decode("utf-8")
            print(f"Setting new state to {tv_state}")
            self.last_state = tv_state
            self.client.publish(self.state_topic, payload=tv_state, qos=1, retain=True)
        else:
            print("Unexpected message received, channel: %s" % message.topic)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)

    def connect(self, addr: str = cfg.broker_addr) -> None:
        self.addr: str = addr
        self.client.connect(self.addr, port=cfg.port)
        self.client.subscribe(self.scheduler_topic)

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    switch = SIISPresence()
    switch.start()
