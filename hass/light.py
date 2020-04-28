# from config_node import *
import paho.mqtt.client as mqtt
import json

# Global variables
# client: mqtt.Client = None
broker_addr: str = "hass.local"
client_name: str = "mqtt_light_1"
base_topic: str = "home/"
set_topic: str = base_topic + client_name + "/set"
state_topic: str = base_topic + client_name + "/state"
available_topic: str = base_topic + client_name + "/available"

last_state: dict = {"state": "OFF"}


def set_state(state: dict):
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


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (broker_addr))
    client.publish(available_topic, payload="online", qos=1, retain=True)
    current_state: str = json.dumps(last_state)
    client.publish(state_topic, current_state, qos=1, retain=True)
    client.subscribe(set_topic)


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    # Check if this is a message that sets the light in a specific config
    if message.topic == set_topic:
        # Load the JSON state
        message_json = json.loads(message.payload)
        print(message_json)
        set_state(message_json)
        # Echo it back
        response = json.dumps(message_json)
        client.publish(state_topic, response, qos=1, retain=True)
    else:
        # This should not happen, we are not subscribed to anything else
        print("Unexpected message received, channel: %s" % message.topic)
    pass


def connect(addr: str = broker_addr) -> mqtt.Client:
    client = mqtt.Client(client_name)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("adrien", "mqttpassword")
    client.will_set(available_topic, payload="offline", qos=1, retain=True)
    client.connect(broker_addr, port=1883)
    return client


# Start polling the files
if __name__ == "__main__":
    client: mqtt.Client = connect(broker_addr)
    client.loop_forever()
