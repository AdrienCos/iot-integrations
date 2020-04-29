# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading
import config as cfg


class SIISHVAC():
    def __init__(self, name: str = "mqtt_hvac_1"):
        self.name: str = name
        self.last_mode: str = ""
        self.last_action: str = "off"
        self.last_target: float = 0
        self.last_temp: float = 20
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.temp_state_topic: str = cfg.base_topic + self.name + "/temperature" + cfg.state_suffix
        self.action_state_topic: str = cfg.base_topic + self.name + "/action" + cfg.state_suffix
        self.mode_set_topic: str = cfg.base_topic + self.name + "/mode" + cfg.set_suffix
        self.mode_state_topic: str = cfg.base_topic + self.name + "/mode" + cfg.state_suffix
        self.target_temperature_set: str = cfg.base_topic + self.name + "/target_temperature" + cfg.set_suffix
        self.target_temperature_state: str = cfg.base_topic + self.name + "/target_temperature" + cfg.state_suffix
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(cfg.username, cfg.password)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

    def get_temp(self) -> float:
        # Replace code here with actual device querying
        if self.last_action == "heating":
            return self.last_temp + round((random.random() * 0.5), 1)
        elif self.last_action == "cooling":
            return self.last_temp - round((random.random() * 0.5), 1)
        else:
            return self.last_temp + round((random.random() * 0.2 - 0.1), 1)

    def start_polling(self) -> None:
        temp: float = self.get_temp()
        self.last_temp = temp
        self.client.publish(self.temp_state_topic, payload=("%0.1f" % (self.last_temp)), qos=1, retain=True)
        if self.last_mode == "cool" and self.last_target < temp:
            payload = "cooling"
        elif self.last_mode == "heat" and self.last_target > temp:
            payload = "heating"
        elif self.last_mode == "fan_only":
            payload = "fan"
        elif self.last_mode == "off":
            payload = "off"
        else:
            payload = "idle"
        print(payload)
        self.last_action = payload
        self.client.publish(self.action_state_topic, payload=self.last_action, qos=1, retain=True)
        threading.Timer(cfg.update_delay, self.start_polling).start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        self.client.publish(self.available_topic, payload="online", qos=1, retain=True)
        self.client.subscribe(self.mode_set_topic)
        self.client.subscribe(self.target_temperature_set)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the light in a specific config
        if message.topic == self.target_temperature_set:
            # Read the target temp
            target_temp: float = float(message.payload)
            print("Setting the target temp at %0.1f" % target_temp)
            self.last_target = target_temp
            # Echo it back
            response = str(target_temp)
            self.client.publish(self.target_temperature_state, response, qos=1, retain=True)
        elif message.topic == self.mode_set_topic:
            # Read the fan setting
            mode_setting: str = message.payload.decode("utf-8")
            print("Setting mode to %s" % mode_setting)
            self.last_mode = mode_setting
            # Echo it back
            response = mode_setting
            self.client.publish(self.mode_state_topic, response, qos=1, retain=True)
        else:
            # This should not happen, we are not subscribed to anything else
            print("Unexpected message received, channel: %s" % message.topic)
        pass

    def connect(self, addr: str = cfg.broker_addr) -> None:
        self.addr: str = addr
        self.client.connect(self.addr, port=cfg.port)


# Start polling the files
if __name__ == "__main__":
    hvac = SIISHVAC()
    hvac.connect()
    hvac.client.loop_start()
    hvac.start_polling()
