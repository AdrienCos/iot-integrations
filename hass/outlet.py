# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg

from siisthing import SIISThing

from hardware.relay import Relay


class SIISOutlet(SIISThing):
    def __init__(self, name: str = "mqtt_outlet_1"):
        self.name: str = name
        SIISThing.__init__(self, name)
        self.last_state: str = ""
        # self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        # self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix
        # self.set_topic: str = cfg.base_topic + self.name + cfg.set_suffix
        # self.client: mqtt.Client = mqtt.Client(self.name)
        # self.client.on_connect = self.on_connect
        # self.client.on_message = self.on_message
        # self.client.tls_set(ca_certs=cfg.cafile,
        #                     certfile=cfg.certfile,
        #                     keyfile=cfg.keyfile)
        # self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

        self.device: Relay = Relay(cfg.pin)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        SIISThing.on_connect(self, client, userdata, flags, rc)
        client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the lock
        if message.topic == self.set_topic or message.topic == self.scheduler_topic:
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

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    lock = SIISOutlet()
    lock.start()
