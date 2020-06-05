# from config_node import *
import paho.mqtt.client as mqtt
import threading
import config as cfg

from siisthing import SIISThing

from hardware.switch import Switch


class SIISSwitch(SIISThing):
    def __init__(self, name: str = "mqtt_switch_1"):
        SIISThing.__init__(self, name)
        self.fixed_state: str

        self.device = Switch(cfg.pin)

    def get_state(self) -> str:
        # Replace code here with actual device querying
        state = self.device.value
        if self.auto_update:
            if state:
                return "ON"
            return "OFF"
        else:
            return self.fixed_state

    def start_polling(self) -> None:
        self.client.publish(self.state_topic, payload=self.get_state(), qos=1, retain=True)
        threading.Timer(cfg.update_delay, self.start_polling).start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        SIISThing.on_connect(self, client, userdata, flags, rc)
        client.publish(self.state_topic, payload=self.get_state(), qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.topic == self.scheduler_topic:
            payload: str = message.payload.decode("utf-8")
            self.auto_update = False
            self.fixed_state = payload
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)

    def start(self):
        self.connect()
        self.client.loop_start()
        self.start_polling()


# Start polling the files
if __name__ == "__main__":
    switch = SIISSwitch()
    switch.start()
