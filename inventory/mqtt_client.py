import paho.mqtt.client as mqtt
import ssl
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# AWS IoT Core Details
AWS_IOT_ENDPOINT = "a3q1z22z5ze4kk-ats.iot.eu-north-1.amazonaws.com"
PORT = 8883
TOPIC = "Realtime/data"

# Paths to certificates
CERTS_PATH = "inventory/certs/"
CA_CERT = CERTS_PATH + "AmazonRootCA1.pem"
DEVICE_CERT = CERTS_PATH + "device.pem.crt"
PRIVATE_KEY = CERTS_PATH + "private.pem.key"

# WebSocket Channel Layer
channel_layer = get_channel_layer()

def on_connect(client, userdata, flags, rc):
    print("Connected to AWS IoT Core with result code: " + str(rc))
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        # Decode and parse JSON data
        payload = msg.payload.decode()
        data = json.loads(payload)

        # Extract relevant fields
        item_data = {
            "ItemID": data.get("ItemID"),
            "ItemName": data.get("ItemName"),
            "Timestamp": data.get("Timestamp"),
            "Quantity": data.get("Quantity"),
            "Units": data.get("Units")
        }

        print(f"Received from MQTT: {item_data}")

        # Send MQTT data to WebSocket
        async_to_sync(channel_layer.group_send)(
            "mqtt_group",
            {
                "type": "send_mqtt_data",
                "data": item_data
            }
        )

    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def mqtt_connect():
    client = mqtt.Client()
    client.tls_set(ca_certs=CA_CERT, certfile=DEVICE_CERT, keyfile=PRIVATE_KEY, tls_version=ssl.PROTOCOL_TLS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(AWS_IOT_ENDPOINT, PORT, keepalive=60)
    client.loop_start()  # Run in background
    return client

# Start MQTT Client
mqtt_client = mqtt_connect()
