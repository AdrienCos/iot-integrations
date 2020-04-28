# from config_node import *
import paho.mqtt.client as mqtt

# Global variables
broker_addr: str = "hass.local"
client_name: str = "mqtt_tv_1"
base_topic: str = "home/"

available_topic: str = base_topic + client_name + "/available"
state_topic: str = base_topic + client_name + "/state"
set_topic: str = base_topic + client_name + "/set"

last_state: str = ""


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print("Connected to MQTT server at %s" % (broker_addr))
    client.publish(available_topic, payload="online", qos=1, retain=True)
    client.publish(state_topic, payload=last_state, qos=1, retain=True)
    client.subscribe(set_topic)


def on_message(client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
    # Check if this is a message that sets the TV
    global last_state
    if message.topic == set_topic:
        # Read the target temp
        tv_state: str = message.payload.decode("utf-8")
        print("Setting the TV to %s" % tv_state)
        last_state = tv_state
        # Echo it back
        response = tv_state
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
