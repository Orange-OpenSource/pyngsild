#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import pytest
import logging

from paho.mqtt.client import MQTTMessage, MQTTMessageInfo, MQTT_ERR_SUCCESS

from pyngsild.utils.mqttclient import MqttClient

logger = logging.getLogger(__name__)

MID: int = 123


@pytest.fixture
def mock_broker(mocker):
    mocker.patch(
        "paho.mqtt.client.Client.connect",
        side_effect=lambda host, port, *_: logger.info(
            f"connect to MQTT broker at {host}:{port}"
        ),
    )
    mocker.patch(
        "paho.mqtt.client.Client.username_pw_set",
        side_effect=lambda user, passwd: logger.info(
            f"set MQTT credentials ({user}, {passwd})"
        ),
    )
    mocker.patch(
        "paho.mqtt.client.Client.subscribe",
        side_effect=lambda topic, qos: (MQTT_ERR_SUCCESS, MID),
    )
    mocker.patch(
        "paho.mqtt.client.Client.publish",
        side_effect=lambda topic, msg, qos: MQTTMessageInfo(MID),
    )
    mocker.patch("paho.mqtt.client.Client.loop_start")
    mocker.patch("paho.mqtt.client.Client.loop_stop")


def callback(msg: MQTTMessage):
    payload = str(msg.payload.decode("utf-8"))


def test_publish(mock_broker):
    mqttc = MqttClient(port=1883)
    res = mqttc.publish(topic="sensor/temperature", msg=22.5)
    mqttc.stop()
    assert res == True


def test_subscribe(mock_broker, mocker):
    mqttc = MqttClient(port=1883, callback=callback)
    mqttc.subscribe(topic="sensor/temperature")

    # create a fake MQTT message
    msg = MQTTMessage(mid=MID)
    msg.topic = b"sensor/temperature"
    msg.payload = b"22.5"

    mocker.spy(mqttc, "callback")

    # trigger 2 messages received on the MQTT bus
    mqttc._client.on_message(mqttc._client, None, msg)
    mqttc._client.on_message(mqttc._client, None, msg)

    mqttc.stop()

    assert mqttc.callback.call_count == 2
