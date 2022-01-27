#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from typing import List

from ngsildclient import Entity

from pyngsild.source import Row
from pyngsild.source.moresources import SourceSample
from pyngsild.sink import Sink, SinkNull
from pyngsild.agent import Agent
from pyngsild.agent.stats import Stats
from pyngsild.agent.processor import build_dummy_entity, build_sample_entity


def test_build_dummy_entity():
    e = build_dummy_entity(Row("dummy"))
    assert e.id == "urn:ngsi-ld:Dummy:Dummy"
    assert e.type == "Dummy"
    assert e["rawData.type"] == "Property"
    assert e["rawData.value"] == "dummy"


def test_build_sample_entity():
    e = build_sample_entity(Row("Room1;21.7;720"))
    assert e.id == "urn:ngsi-ld:RoomTemperatureObserved:Room1"
    assert e.type == "RoomTemperatureObserved"
    assert e["temperature.value"] == 21.7
    assert e["pressure.value"] == 720


def test_agent_no_process(mocker):
    src = SourceSample(count=5, delay=0)
    sink = SinkNull()
    mocker.spy(sink, "write")
    agent = Agent(src, sink)
    agent.run()
    agent.close()
    assert sink.write.call_count == 5
    assert agent.stats == Stats(5, 5, 5, 0, 0)


def test_agent(mocker):
    src = SourceSample(count=5, delay=0)
    sink = SinkNull()
    mocker.spy(sink, "write")
    agent = Agent(src, sink, build_sample_entity)
    agent.run()
    agent.close()
    assert sink.write.call_count == 5
    assert agent.stats == Stats(5, 5, 5, 0, 0)


def test_agent_with_side_effect(mocker):
    def side_effect(row: Row, sink: Sink, entity: Entity):
        # each time we acquire data from sensors in a room, we create (or override) a side-entity
        # here the side-entity is a room entity for a Building datamodel
        e = Entity(f"Building:MainBuilding:Room:{entity.id}")
        sink.write(e)
        return 1  # number of entities created in the function

    src = SourceSample(count=5, delay=0)
    sink = SinkNull()
    mocker.spy(sink, "write")
    agent = Agent(src, sink, build_sample_entity, side_effect)
    agent.run()
    agent.close()
    assert sink.write.call_count == 10
    assert agent.stats == Stats(5, 5, 5, 0, 0, 5)
