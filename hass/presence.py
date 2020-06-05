# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg

from siisthing import SIISThing

from hardware.pir import PIR


class SIISPresence(SIISThing):
    def __init__(self, name: str = "mqtt_presence_1"):
        SIISThing.__init__(self, name)
        self.last_state: str = "OFF"

        self.device: PIR = PIR(cfg.pin, self.activated, self.deactivated)

    def activated(self) -> None:
        pass

    def deactivated(self) -> None:
        pass

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            state = message.payload.decode("utf-8")
            print(f"Setting new state to {state}")
            self.last_state = state
            self.client.publish(self.state_topic, payload=state, qos=1, retain=True)
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        SIISThing.on_connect(self, client, userdata, flags, rc)
        client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    switch = SIISPresence()
    switch.start()
