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
import signal
import logging

from paho.mqtt.client import MQTTMessage
from queue import SimpleQueue as Queue
from typing import Union, Sequence, Tuple, Literal

from . import Source, Row, ROW_NOT_SET as QUEUE_EOT
from pyngsild.utils.mqttclient import MqttClient, MQTT_DEFAULT_PORT

logger = logging.getLogger(__name__)

OneOrManyStrings = Union[str, Sequence[str]]


class SourceMqtt(Source):
    """A SourceMqtt receives data from a MQTT broker on a given topic.

    Each time a message is received on the subscribed topic(s), the Source emits a Row composed of the message payload.
    The row provider is set to the topic.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = MQTT_DEFAULT_PORT,
        credentials: Tuple[str, str] = (None, None),
        topic: OneOrManyStrings = "#",  # all topics
        qos: Literal[0, 1, 2] = 0,  # no ack
    ):
        """Returns a SourceMqtt instance.

        Args:
            host (str): Hostname or IP address of the remote broker. Defaults to "localhost".
            port (int): Network port of the server host to connect to. Defaults to 1883.
            credentials (str,str): Username and password used in broker authentication. Defaults to no auth.
            topic (OneOrManyStrings): Topic (or list of topics) to subscribe to. Defaults to "#" (all topics).
            qos (Literal[0, 1, 2]) : QoS : 0, 1 or 2 according to the MQTT protocol. Defaults to 0 (no ack).

        """
        self.topic = topic
        self._queue: "Queue[Row]" = Queue()
        user, passwd = credentials
        self._mcsub: MqttClient = MqttClient(
            host, port, user, passwd, qos, callback=self._callback
        )
        # install signal hooks
        try:
            signal.signal(signal.SIGINT, self._handle_signal)
            signal.signal(signal.SIGQUIT, self._handle_signal)
            signal.signal(signal.SIGTERM, self._handle_signal)
        except ValueError as e:
            logger.warning(e)

    def __iter__(self):
        self._mcsub.subscribe(self.topic)
        while True:
            row: Row = self._queue.get(True)
            if row == QUEUE_EOT:  # End Of Transmission
                logger.info("Received EOT")
                break
            yield row
        self._mcsub.stop()

    def _callback(self, msg: MQTTMessage):
        payload = str(msg.payload.decode("utf-8"))
        self._queue.put(Row(msg.topic, payload))

    def _handle_signal(self, signum, frame):
        """Properly clean resources when a signal is received"""
        logger.info("Received SIGNAL : ")
        logger.info("Stopping loop...")
        self._queue.put(QUEUE_EOT)
        time.sleep(1)

    def close(self):
        """Properly disconnect from MQTT broker and free resources"""
        self._queue.put(QUEUE_EOT)
        self._mcsub.stop()
