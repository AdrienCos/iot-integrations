# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg

from siisthing import SIISThing

from hardware.servo import ServoMotor


class SIISLock(SIISThing):
    def __init__(self, name: str = "mqtt_lock_1"):
        SIISThing.__init__(self, name)
        self.last_state: str = ""

        self.device: ServoMotor = ServoMotor(cfg.pin)
        self.connect()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        # Extend the on_connect method of SIISThing
        SIISThing.on_connect(self, client, userdata, flags, rc)
        self.client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)

    def set_state(self, state: str) -> None:
        if state == "ON":
            self.device.on()
        elif state == "OFF":
            self.device.off()
        else:
            print("Invalid state")
        self.last_state = state

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the lock
        if message.topic == self.set_topic or message.topic == self.scheduler_topic:
            # Read the target state
            lock: str = message.payload.decode("utf-8")
            print("Setting the lock to %s" % lock)
            self.last_state = lock
            # Echo it back
            response = lock
            client.publish(self.state_topic, response, qos=1, retain=True)
        else:
            # Pass the message down
            SIISThing.on_message(self, client, userdata, message)

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    lock = SIISLock()
    lock.start()
