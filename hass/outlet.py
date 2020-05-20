# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg

from hardware.relay import Relay


class SIISOutlet():
    def __init__(self, name: str = "mqtt_outlet_1"):
        self.name: str = name
        self.last_state: str = ""
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix
        self.set_topic: str = cfg.base_topic + self.name + cfg.set_suffix
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(cfg.username, cfg.password)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

        self.device: Relay = Relay(cfg.pin)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)
        client.subscribe(self.set_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the lock
        if message.topic == self.set_topic:
            # Read the target temp
            outlet: str = message.payload.decode("utf-8")
            print("Setting the outlet to %s" % outlet)
            self.last_state = outlet
            # Echo it back
            response = outlet
            client.publish(self.state_topic, response, qos=1, retain=True)
        else:
            # This should not happen, we are not subscribed to anything else
            print("Unexpected message received, channel: %s" % message.topic)
        pass

    def set_state(self, state: str) -> None:
        if state == "ON":
            self.device.set()
        elif state == "OFF":
            self.device.unset()
        else:
            print("Invalid state")
        self.last_state = state

    def connect(self, addr: str = cfg.broker_addr) -> mqtt.Client:
        self.addr: str = addr
        self.client.connect(addr, port=1883)

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    lock = SIISOutlet()
    lock.start()
