# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg

from siisthing import SIISThing

from hardware.tv import TV


class SIISTV(SIISThing):
    def __init__(self, name: str = "mqtt_tv_1"):
        SIISThing.__init__(self, name)
        self.last_state: str = ""

        self.device: TV = TV()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        SIISThing.on_connect(self, client, userdata, flags, rc)
        self.client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the TV
        if message.topic == self.set_topic:
            # Read the target temp
            tv_state: str = message.payload.decode("utf-8")
            print("Setting the TV to %s" % tv_state)
            self.set_state(tv_state)
            # Echo it back
            response = tv_state
            self.client.publish(self.state_topic, response, qos=1, retain=True)
        elif message.topic == self.scheduler_topic:
            tv_state = message.payload.decode("utf-8")
            print(f"Received message from Scheduler, setting new state to {tv_state}")
            self.set_state(tv_state)
            # Publish the state to Hass
            response = tv_state
            self.client.publish(self.state_topic, response, qos=1, retain=True)
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def set_state(self, state: str) -> None:
        if state == "ON":
            self.device.on()
        elif state == "OFF":
            self.device.off()
        else:
            print("Invalid state")
        self.last_state = state

    def connect(self, addr: str = cfg.broker_addr) -> None:
        self.addr: str = addr
        self.client.connect(self.addr, port=cfg.port)

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    tv = SIISTV()
    tv.start()
