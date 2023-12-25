from flask import Flask, request, Response
import threading
import paho.mqtt.client as mqtt
import json
import os
import time

app = Flask(__name__)

# File paths for storing data
http_output_file = "http_info.json"
mqtt_output_file = "mqtt_info.json"
map_output_file = "map_info.json"

# MQTT Broker details
MQTT_BROKER = "nam1.cloud.thethings.network"
MQTT_PORT = 1883
MQTT_USERNAME = "irt-lora-app@ttn"
MQTT_PASSWORD = "NNSXS.JE6XVMLMCELW6FLICEXHHMHXU4WJRW4XMUURKGQ.K2R3JYCRTTDZJUCAENOSNSIZY6WA2B2M3PZPES5GHHRXMXFOBV3Q"
MQTT_TOPIC = "#"


# Function to read JSON data from a file
def read_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    else:
        return []

# Function to write JSON data to a file
def write_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to append new data to JSON file for HTTP stream
def append_to_json_file(file_path, new_data):
    data = read_json_file(file_path)
    data.append(new_data)
    write_json_file(file_path, data)

# Function to append new data to JSON file for MQTT stream, with duplicate check
def mqtt_append_with_check(file_path, new_data):
    data = read_json_file(file_path)
    if not data or data[-1] != new_data:
        data.append(new_data)
    write_json_file(file_path, data)

# MQTT Client Setup
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    new_data = json.loads(message)
    mqtt_append_with_check(mqtt_output_file, new_data)
    print("New MQTT message")

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

# Flask route for handling HTTP POST requests
@app.route('/', methods=['POST'])
def handle_post_request():
    data = json.loads(request.data.decode('utf-8'))
    append_to_json_file(http_output_file, data)
    
    # Call Process mapping asynchronously so as to not block new streams
    threading.Thread(target=process_and_print_result, args=(data,)).start()
    
    return Response(status=200)

# Flask route for handling HTTP GET requests
@app.route('/', methods=['GET'])
def handle_get_request():
    try:
        with open(map_output_file, 'r') as file:
            content = file.read()
        return Response(content, status=200, content_type='application/json')
    except FileNotFoundError:
        return "File not found", 404

def process_and_print_result(data):
    #sleep a few seconds to allow for lags in the mqtt processing
    time.sleep(3) 
    result = process_gateway_data(data)
    print(f"\n\nMapping Process Result: {result}\n\n")

def process_gateway_data(arg_json):
    # Check for 'gateways' key and find the specific gateway
    gateways = arg_json.get('gateways', [])
    target_timestamp = None
    for gateway in gateways:
        if gateway.get('gtw_id') == 'irt-mudd-rooftop-gateway':
            target_timestamp = gateway.get('timestamp')
            break

    if target_timestamp is None:
        return "no match"

    # Read from mqtt_output_file and find a matching timestamp
    mqtt_data = read_json_file(mqtt_output_file)
    match_found = False
    for mqtt_entry in reversed(mqtt_data[-5:]):  # Check last 5 entries
        rx_metadata = mqtt_entry.get('uplink_message', {}).get('rx_metadata', [])
        for index, metadata in enumerate(rx_metadata):
            if metadata.get('timestamp') == target_timestamp:
                match_found = True
                # Get values from arg_json and mqtt_entry
                latitude = arg_json.get('latitude')
                longitude = arg_json.get('longitude')
                altitude = arg_json.get('altitude')
                accuracy = arg_json.get('accuracy_meters')
                payload = mqtt_entry.get('uplink_message', {}).get('decoded_payload', {})
                rssi = metadata.get('rssi')
                snr = metadata.get('snr')
                channel_rssi = metadata.get('channel_rssi')
                channel_index = metadata.get('channel_index')
                gps_time = metadata.get('gps_time')

                # Construct new JSON object
                new_json = {
                    "timestamp": target_timestamp,
                    "gps_time": gps_time,
                    "rssi": rssi,
                    "snr": snr,
                    "channel_rssi": channel_rssi,
                    "channel_index": channel_index,
                    "payload": payload,
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude,
                    "accuracy": accuracy
                }

                # Append to map_output_file
                append_to_json_file(map_output_file, new_json)
                

                return "mapped"
    
    return "no match" if not match_found else "error"

if __name__ == '__main__':
    #app.run(host='172.17.0.1', debug=True) ##DEBUG
    app.run(host='172.17.0.1')
