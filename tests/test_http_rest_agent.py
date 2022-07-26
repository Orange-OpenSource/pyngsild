#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import pkg_resources

from fastapi.testclient import TestClient

from pyngsild.agent.bg.http_rest import HttpRestAgent

# from pyngsild.agent.processor import build_sample_entity
from pyngsild.agent.stats import Stats
from pyngsild import Row
from ngsildclient import Entity
from pydantic import BaseModel


class RoomObserved(BaseModel):
    room: int
    temperature: int
    pressure: float


def process(row: Row) -> Entity:
    room: RoomObserved = row.record
    e = Entity("RoomTemperatureObserved", f"Room{room.room}")
    e.prop("temperature", room.temperature)
    e.prop("pressure", room.pressure)
    return e


agent = HttpRestAgent(process=process)
client = TestClient(agent.app)


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "pyngsild-0.1.1"}


def test_endpoint():

    response = client.post(
        "/rooms/", json={"room": 1, "temperature": 23, "pressure": 710.0}
    )
    assert response.status_code == 201
    assert agent.stats == Stats(1, 1, 1, 0, 0)
    assert agent.status.calls == 1
    assert agent.status.success == 1
