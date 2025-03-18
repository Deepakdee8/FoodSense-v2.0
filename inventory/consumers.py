# import json
# import asyncio
# import paho.mqtt.client as mqtt
# from channels.generic.websocket import AsyncWebsocketConsumer

# AWS_IOT_ENDPOINT = "xxxxxx-ats.iot.region.amazonaws.com"
# AWS_IOT_TOPIC = ""

# class IoTConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()
#         self.client = mqtt.Client()
#         self.client.on_connect = self.on_connect
#         self.client.on_message = self.on_message

#         # Connect to AWS IoT Core over WebSockets
#         self.client.ws_set_options(path="/mqtt", headers=None)
#         self.client.connect(AWS_IOT_ENDPOINT, 443, 60)
#         self.client.loop_start()

#     def on_connect(self, client, userdata, flags, rc):
#         print("Connected to AWS IoT Core")
#         client.subscribe(AWS_IOT_TOPIC)

#     def on_message(self, client, userdata, msg):
#         asyncio.run(self.send(json.dumps({"topic": msg.topic, "message": msg.payload.decode()})))

#     async def disconnect(self, close_code):
#         self.client.loop_stop()
#         self.client.disconnect()


import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MQTTConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("mqtt_group", self.channel_name)
        print("WebSocket Connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("mqtt_group", self.channel_name)
        print("WebSocket Disconnected")

    async def send_mqtt_data(self, event):
        data = event["data"]
        await self.send(text_data=json.dumps({"message": data}))
