#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from fastapi.testclient import TestClient
from pydantic import BaseModel

from pyngsild.agent.bg.http_rest import HttpRestAgent
from pyngsild.agent.stats import Stats
from pyngsild import Row
from ngsildclient import *


class AgriParcel(BaseModel):
    id: str
    date: str
    moisture: int


def build_entity_json(row: Row) -> Entity:
    parcel: AgriParcel = row.record
    e = Entity("AgriParcelRecord", parcel.id)
    e.obs(parcel.date)
    e.prop("soilMoistureVwc", parcel.moisture, observedat=Auto, unitcode="C62")
    return e

agent = HttpRestAgent(process=build_entity_json, endpoint="/moisture/", mtype=AgriParcel)
client = TestClient(agent.app)


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "pyngsild-0.1.1"}


def test_endpoint():
    response = client.post(
        "/moisture/", json={"id": "parcel:001", "date": "2022-07-25T09:00:12Z", "moisture": 75}
    )
    assert response.status_code == 201
    assert agent.stats == Stats(1, 1, 1, 0, 0)
    assert agent.status.calls == 1
    assert agent.status.success == 1
