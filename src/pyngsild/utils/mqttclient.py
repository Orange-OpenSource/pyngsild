#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import time
import logging

from paho.mqtt import client as pahoclient
from paho.mqtt.client import MQTTMessage, MQTTMessageInfo, MQTT_ERR_SUCCESS
from shortuuid import uuid
from typing import Any, Callable, Literal

from pyngsild.__init__ import __version__

logger = logging.getLogger(__name__)

MQTT_DEFAULT_PORT = 1883
MQTT_CONNECT_RC = [
    "Connection accepted",  # 0x0
    "The Server does not support the level of the MQTT protocol requested by the Client",  # 0x1
    "The Client identifier is correct UTF-8 but not allowed by the Server",  # 0x2
    "The Network Connection has been made but the MQTT service is unavailable",  # 0x3
    "The data in the user name or password is malformed",  # 0x4
    "The Client is not authorized to connect",  # 0x5
    "Reserved for future use",  # 0x6-0xff
]


class MqttError(Exception):
    pass


class MqttNotConnectedError(MqttError):
    pass


class MqttConnectionError(MqttError):
    pass


class MqttClient:
    def __init__(
        self,
        host: str = "localhost",
        port: int = MQTT_DEFAULT_PORT,
        user: str = None,
        passwd: str = None,
        qos: Literal[0, 1, 2] = 0,
        callback: Callable[[MQTTMessage], None] = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.qos = qos
        self.callback = callback
        self.id = f"pyngsild-{__version__}-mqtt-client-{uuid()}"
        self._connect()
        self.start()
        logger.info(f"Created MqttClient instance {self.id}")

    def _connect(self):
        self._client = pahoclient.Client(self.id)
        # plug callbacks
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_publish = self._on_publish
        self._client.on_log = self._on_log
        self._client.on_disconnect = self._on_disconnect
        self._client.on_subscribe = self._on_subscribe
        self._client.on_unsubscribe = self._on_unsubscribe
        if self.user is not None:
            self._client.username_pw_set(self.user, self.passwd)
        try:
            self._client.connect(self.host, self.port)
        except Exception as e:
            raise MqttConnectionError() from e

    def _disconnect(self):
        if self._client is None:
            raise MqttNotConnectedError()
        self._client.disconnect()

    def subscribe(self, topic: str):
        if self._client is None:
            raise MqttNotConnectedError()
        rc, mid = self._client.subscribe(topic, qos=self.qos)
        if rc == MQTT_ERR_SUCCESS:
            logger.info(f"[{self.id}][#{mid}] Subscribed to topic {topic}")
        else:
            logger.error(f"[{self.id}][#{mid}] Failed to subscribe to topic {topic}")

    def unsubscribe(self, topic: str):
        if self._client is None:
            raise MqttNotConnectedError()
        rc, mid = self._client.unsubscribe(topic)
        if rc == MQTT_ERR_SUCCESS:
            logger.info(f"[{self.id}][#{mid}] Unsubscribed from topic {topic}")
        else:
            logger.error(
                f"[{self.id}][#{mid}] Failed to unsubscribe from topic {topic}"
            )

    def publish(self, topic: str, msg: str) -> bool:
        if self._client is None:
            raise MqttNotConnectedError()
        status: MQTTMessageInfo = self._client.publish(topic, msg, self.qos)
        if status.rc == MQTT_ERR_SUCCESS:
            logger.debug(
                f"[{self.id}][#{status.mid}] Message {msg} published to {topic}"
            )
            return True
        else:
            logger.error(
                f"[{self.id}][#{status.mid}] Cannot publish {msg} to {topic} : RC={status.rc}"
            )
            return False

    def _on_connect(self, client: pahoclient, userdata: Any, flags: dict, rc: int):
        if rc == 0:
            logger.info(f"[{self.id}]Connected to MQTT broker !")
        elif rc < 6:
            raise MqttConnectionError(MQTT_CONNECT_RC)
        else:
            raise MqttConnectionError(6)

    def _on_message(self, client: pahoclient, userdata: Any, msg: MQTTMessage):
        payload = str(msg.payload.decode("utf-8"))
        logger.debug(
            f"[{self.id}][#{msg.mid}] Received message {payload} from {msg.topic}"
        )
        if self.callback:
            self.callback(msg)

    def _on_publish(self, client: pahoclient, userdata: Any, mid: int):
        logger.debug(f"[{self.id}][#{mid}] Broker acked publication")

    def _on_log(self, client: pahoclient, userdata: Any, level, buf):
        logger.trace(f"[{self.id}] {buf}")

    def _on_disconnect(self, client: pahoclient, userdata: Any, rc: int):
        if rc == MQTT_ERR_SUCCESS:
            logger.info(f"[{self.id}] Disconnected from MQTT broker")
        else:
            logger.warning(f"[{self.id}] Failed to disconnect from MQTT broker : {rc=}")

    def _on_subscribe(
        self, client: pahoclient, userdata: Any, mid: int, granted_qos: int
    ):
        logger.info(f"[{self.id}][#{mid}] Brocker acked subscription")

    def _on_unsubscribe(self, client: pahoclient, userdata: Any, mid: int):
        logger.info(f"[{self.id}][#{mid}] Brocker acked unsubscription")

    def start(self):
        self._client.loop_start()

    def stop(self):
        self._disconnect()
        self._client.loop_stop()


def main():
    def new_client():
        return MqttClient(qos=2)

    mcpub, mcsub = mqttc = [new_client(), new_client()]
    topic = "sensor/temperature"

    mcsub.subscribe(topic)

    for i in range(10):
        mcpub.publish(topic, i + 12)
        if i == 5:
            mcsub.unsubscribe(topic)
        time.sleep(1)

    for mc in mqttc:
        mc.stop()


if __name__ == "__main__":
    main()
