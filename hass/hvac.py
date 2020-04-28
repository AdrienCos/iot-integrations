# from config_node import *
import paho.mqtt.client as mqtt
import random
import threading

# Global variables
broker_addr: str = "hass.local"
client_name: str = "mqtt_hvac_1"
base_topic: str = "home/"
available_topic: str = base_topic + client_name + "/available"
action_state_topic: str = base_topic + client_name + "/action" + "/state"
mode_set_topic: str = base_topic + client_name + "/mode" + "/set"
mode_state_topic: str = base_topic + client_name + "/mode" + "/state"
temp_state_topic: str = base_topic + client_name + "/temperature" + "/state"
target_temperature_set: str = base_topic + client_name + "/target_temperature" + "/set"
target_temperature_state: str = base_topic + client_name + "/target_temperature" + "/state"

update_delay: float = 1

last_mode: str = ""
last_target: float = 0


def get_temp() -> float:
    # Replace code here with actual device querying
    return random.random() * 2 + 20


def start_polling(client: mqtt.Client) -> None:
    temp: float = get_temp()
    client.publish(temp_state_topic, payload=("%0.1f" % (temp)), qos=1, retain=True)
    if last_mode == "cool" and last_target < temp:
        payload = "cooling"
    elif last_mode == "heat" and last_target > temp:
        payload = "heating"
    elif last_mode == "fan_only":
        payload = "fan"
    elif last_mode == "off":
        payload = "off"
    else:
        payload = "idle"
    client.publish(action_state_topic, payload=payload, qos=1, retain=True)
    threading.Timer(update_delay, start_polling, [client]).start()


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (broker_addr))
    client.publish(available_topic, payload="online", qos=1, retain=True)
    client.subscribe(mode_set_topic)
    client.subscribe(target_temperature_set)


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    # Check if this is a message that sets the light in a specific config
    global last_target, last_mode
    if message.topic == target_temperature_set:
        # Read the target temp
        target_temp: float = float(message.payload)
        print("Setting the target temp at %0.1f" % target_temp)
        last_target = target_temp
        # Echo it back
        response = str(target_temp)
        client.publish(target_temperature_state, response, qos=1, retain=True)
    elif message.topic == mode_set_topic:
        # Read the fan setting
        mode_setting: str = message.payload.decode("utf-8")
        print("Setting mode to %s" % mode_setting)
        last_mode = mode_setting
        # Echo it back
        response = mode_setting
        client.publish(mode_state_topic, response, qos=1, retain=True)
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
    client.loop_start()
    start_polling(client)
