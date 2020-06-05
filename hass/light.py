# from config_node import *
import paho.mqtt.client as mqtt
import json
import config as cfg

from siisthing import SIISThing

from hardware.light import RGBLight


class SIISLight(SIISThing):
    def __init__(self, name: str = "mqtt_light_1"):
        SIISThing.__init__(self, name)
        self.last_state: dict = {"state": "OFF"}

        self.device: RGBLight = RGBLight(cfg.pin)

    def set_state(self, state: dict):
        if state["state"] == "ON":
            # Check if we have some RGB instructions
            if ("color" in state.keys()) and ("r" in state["color"].keys()):
                print("Setting lamp in RGB mode")
                r: int = int(state["color"]["r"])
                g: int = int(state["color"]["g"])
                b: int = int(state["color"]["b"])

                # Set the RGB value of the lamp
                self.device.color = (r, g, b)
            elif "brightness" in state.keys():
                print("Setting the lamp in brightness mode")
                brightness: int = int(state["brightness"])
                # Set the brightness of the lamp
                self.device.brightness = brightness
            elif "color_temp" in state.keys():
                print("Setting the lamp in temperature mode")
                temp: int = int(state["color_temp"])
                # Set the temperature of the lamp
                self.device.temperature = temp
            else:
                print("Turning on the lamp")
                # Set the lamp to full setting
                self.device.on()
        else:
            print("Turning off the lamp")
            # Turn off the lamp
            self.device.off()
        self.last_state = state

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        SIISThing.on_connect(self, client, userdata, flags, rc)
        current_state: str = json.dumps(self.last_state)
        self.client.publish(self.state_topic, current_state, qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        # Check if this is a message that sets the light in a specific config
        if message.topic == self.set_topic:
            # Load the JSON state
            message_json = json.loads(message.payload)
            self.set_state(message_json)
            # Echo it back
            response = json.dumps(message_json)
            self.client.publish(self.state_topic, response, qos=1, retain=True)
        elif message.topic == self.scheduler_topic:
            payload = message.payload.decode("utf-8")
            if payload == "ON":
                self.device.on()
            elif payload == "OFF":
                self.device.off()
            elif payload == "BRI":
                self.device.brightness = 100
            elif payload == "TEMP":
                self.device.temperature
            elif payload == "COL":
                self.device.color = (19, 2, 150)
        else:
            # Pass it down
            SIISThing.on_message(self, client, userdata, message)
        return

    def start(self):
        self.connect()
        self.client.loop_forever()


# Start polling the files
if __name__ == "__main__":
    light = SIISLight()
    light.start()
