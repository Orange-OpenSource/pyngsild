#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.


import threading
import logging
import anyio

from datetime import datetime
from paho.mqtt.client import MQTTMessage
from queue import SimpleQueue as Queue
from typing import Literal, Callable

from pyngsild.source import Row, ROW_NOT_SET as QUEUE_EOT, SourceSingle
from pyngsild.utils.mqttclient import MqttClient, MQTT_DEFAULT_PORT
from pyngsild.sink import *
from . import ManagedDaemon

logger = logging.getLogger(__name__)


class MqttAgent(ManagedDaemon):
    """A MqttAgent receives data from a MQTT broker on a given topic.

    Each time a message is received on the subscribed topic(s), the Source emits a Row composed of the message payload.
    The row provider is set to the topic.
    """

    def __init__(
        self,
        sink: Sink = SinkStdout(),
        process: Callable[[Row]] = lambda row: row.record,
        host: str = "localhost",
        port: int = MQTT_DEFAULT_PORT,
        credentials: tuple[str, str] = (None, None),
        topic: str | list[str] = "#",  # all topics
        qos: Literal[0, 1, 2] = 0,  # no ack
    ):
        """Returns a MqttAgent instance.

        Args:
            host (str): Hostname or IP address of the remote broker. Defaults to "localhost".
            port (int): Network port of the server host to connect to. Defaults to 1883.
            credentials (str,str): Username and password used in broker authentication. Defaults to no auth.
            topic (OneOrManyStrings): Topic (or list of topics) to subscribe to. Defaults to "#" (all topics).
            qos (Literal[0, 1, 2]) : QoS : 0, 1 or 2 according to the MQTT protocol. Defaults to 0 (no ack).

        """
        super().__init__(sink, process)
        self.topic = topic
        self._queue: Queue[Row] = Queue()
        user, passwd = credentials
        self._mcsub: MqttClient = MqttClient(
            host, port, user, passwd, qos, callback=self._callback
        )

    async def _aloop(self):
        while True:
            row: Row = self._queue.get(True)
            if row == QUEUE_EOT:  # End Of Transmission
                logger.info("Received EOT")
                break
            src = SourceSingle(row, provider="mqtt")
            await self.trigger(src)  # TODO => sync it or all async
        logger.info("EOT received !")
        self._mcsub.stop()

    def _loop(self):
        anyio.run(self._aloop)

    def run(self):
        super().run()
        self._mcsub.subscribe(self.topic)
        thread = threading.Thread(target=self._loop)
        thread.start()

    def _callback(self, msg: MQTTMessage):
        logger.debug(f"Received MQTT message : {msg}")
        self.status.lastcalltime = datetime.now()
        self.status.calls += 1
        payload = str(msg.payload.decode("utf-8"))
        self._queue.put(Row(msg.topic, payload))

    def close(self):
        """Properly disconnect from MQTT broker and free resources"""
        self._queue.put(QUEUE_EOT)
        self._mcsub.stop()
        super().close()
