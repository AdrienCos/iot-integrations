# from config_node import *
import paho.mqtt.client as mqtt
import config as cfg


class SIISLock():
    def __init__(self, name: str = "mqtt_lock_1"):
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

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        client.publish(self.available_topic, payload="online", qos=1, retain=True)
        client.publish(self.state_topic, payload=self.last_state, qos=1, retain=True)
        client.subscribe(self.set_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the lock
        if message.topic == self.set_topic:
            # Read the target temp
            lock: str = message.payload.decode("utf-8")
            print("Setting the lock to %s" % lock)
            self.last_state = lock
            # Echo it back
            response = lock
            client.publish(self.state_topic, response, qos=1, retain=True)
        else:
            # This should not happen, we are not subscribed to anything else
            print("Unexpected message received, channel: %s" % message.topic)
        pass

    def connect(self, addr: str = cfg.broker_addr) -> mqtt.Client:
        self.addr: str = addr
        self.client.connect(addr, port=1883)


# Start polling the files
if __name__ == "__main__":
    lock = SIISLock()
    lock.connect()
    lock.client.loop_forever()
