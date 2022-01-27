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
import threading

from pyngsild.source.sourcemqtt import SourceMqtt
from pyngsild.source import Row


@pytest.fixture
def mock_mqttclient(mocker):
    mocker.patch("pyngsild.source.sourcemqtt.MqttClient")


def publisher(src: SourceMqtt):
    for temp in range(5):
        src._queue.put(Row("sensor/temperature", temp))
        # time.sleep(1)


def subscriber(src: SourceMqtt):
    for x in src:
        src.counter += 1
        print(x)


def test_receive(mock_mqttclient):
    src = SourceMqtt(topic="sensor/temperature")

    src.counter = 0
    pub = threading.Thread(target=publisher, args=[src])
    sub = threading.Thread(target=subscriber, args=[src])
    pub.start()
    sub.start()

    pub.join()
    src.close()
    sub.join()

    assert src.counter == 5
