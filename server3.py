from flask import Flask, request, Response
import threading
import paho.mqtt.client as mqtt

app = Flask(__name__)

# File paths for storing data
http_output_file = "http_info.txt"
mqtt_output_file = "mqtt_info.txt"

# MQTT Broker details
MQTT_BROKER = "nam1.cloud.thethings.network"
MQTT_PORT = 1883
MQTT_USERNAME = "irt-lora-app@ttn"
MQTT_PASSWORD = "NNSXS.JE6XVMLMCELW6FLICEXHHMHXU4WJRW4XMUURKGQ.K2R3JYCRTTDZJUCAENOSNSIZY6WA2B2M3PZPES5GHHRXMXFOBV3Q"
MQTT_TOPIC = "#"


# MQTT Client Setup
is_subscribed = False
def on_connect(client, userdata, flags, rc):
    global is_subscribed
    print("Connected with result code " + str(rc))
    if not is_subscribed:
        client.subscribe(MQTT_TOPIC)
        is_subscribed = True


def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"MQTT message received: {message}")
    with open(mqtt_output_file, 'a') as file:
        file.write(message + '\n')

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Function to start the MQTT client
def start_mqtt_client():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

# Start MQTT client in a separate thread
threading.Thread(target=start_mqtt_client, daemon=True).start()

# Flask routes for handling HTTP requests
@app.route('/', methods=['POST'])
def handle_post_request():
    data = request.data.decode('utf-8')
    with open(http_output_file, 'a') as file:
        file.write(data + '\n')
    return Response(status=200)

@app.route('/', methods=['GET'])
def handle_get_request():
    try:
        with open(http_output_file, 'r') as file:
            content = file.read()
        return Response(content, status=200, content_type='text/plain')
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(host='172.17.0.1', debug=True)
