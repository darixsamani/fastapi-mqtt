from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi_mqtt.config import MQTTConfig
from fastapi_mqtt.fastmqtt import FastMQTT

mqtt_config = MQTTConfig(
    will_message_topic="/WILL",
    will_message_payload="MQTT Connection is dead!",
    will_delay_interval=2,
)

fast_mqtt = FastMQTT(config=mqtt_config)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    await fast_mqtt.mqtt_startup()
    yield
    await fast_mqtt.mqtt_shutdown()


app = FastAPI(lifespan=_lifespan)


@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    fast_mqtt.client.subscribe("/WILL")  # /WILL will trigger after disconnect
    fast_mqtt.client.subscribe("/mqtt")
    print("Connected: ", client, flags, rc, properties)


@fast_mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ", topic, payload.decode(), qos, properties)

    return 0


@fast_mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")


@fast_mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("subscribed", client, mid, qos, properties)


@app.get("/")
async def func():
    # publishing mqtt topic
    fast_mqtt.publish("/mqtt", "Hello from Fastapi")
    return {"result": True, "message": "Published"}
