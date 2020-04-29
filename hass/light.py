# from config_node import *
import paho.mqtt.client as mqtt
import json
import config as cfg

# Global variables
# client: mqtt.Client = None
# broker_addr: str = "hass.local"
# client_name: str = "mqtt_light_1"
# base_topic: str = "home/"
# set_topic: str = base_topic + client_name + "/set"
# state_topic: str = base_topic + client_name + "/state"
# available_topic: str = base_topic + client_name + "/available"

# last_state: dict = {"state": "OFF"}


class SIISLight():
    def __init__(self, name: str = "mqtt_light_1"):
        self.name: str = name
        self.last_state: dict = {"state": "OFF"}
        self.available_topic: str = cfg.base_topic + self.name + cfg.available_suffix
        self.state_topic: str = cfg.base_topic + self.name + cfg.state_suffix
        self.set_topic: str = cfg.base_topic + self.name + cfg.set_suffix
        self.client: mqtt.Client = mqtt.Client(self.name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(cfg.username, cfg.password)
        self.client.will_set(self.available_topic, payload=cfg.offline_payload, qos=1, retain=True)

    def set_state(self, state: dict):
        if state["state"] == "ON":
            # Check if we have some RGB instructions
            if ("color" in state.keys()) and ("r" in state["color"].keys()):
                print("Setting lamp in RGB mode")
                r: int = int(state["color"]["r"])
                g: int = int(state["color"]["g"])
                b: int = int(state["color"]["b"])
                # Set the RGB value of the lamp
                _ = r + g + b
            elif "brightness" in state.keys():
                print("Setting the lamp in brightness mode")
                brightness: int = int(state["brightness"])
                # Set the brightness of the lamp
                _ = brightness
            elif "color_temp" in state.keys():
                print("Setting the lamp in temperature mode")
                temp: int = int(state["color_temp"])
                # Set the temperature of the lamp
                _ = temp
            else:
                print("Turning on the lamp")
                # Set the lamp to full setting
                pass
        else:
            print("Turning off the lamp")
            # Turn off the lamp
            pass
        self.last_state = state

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT server at %s" % (self.addr))
        self.client.publish(self.available_topic, payload=cfg.online_payload, qos=1, retain=True)
        current_state: str = json.dumps(self.last_state)
        self.client.publish(self.state_topic, current_state, qos=1, retain=True)
        self.client.subscribe(self.set_topic)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the light in a specific config
        if message.topic == self.set_topic:
            # Load the JSON state
            message_json = json.loads(message.payload)
            print(message_json)
            self.set_state(message_json)
            # Echo it back
            response = json.dumps(message_json)
            self.client.publish(self.state_topic, response, qos=1, retain=True)
        else:
            # This should not happen, we are not subscribed to anything else
            print("Unexpected message received, channel: %s" % message.topic)
        return

    def connect(self, addr: str = cfg.broker_addr) -> None:
        self.addr: str = addr
        self.client.connect(self.addr, port=1883)

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    light = SIISLight()
    light.start()
