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

from pyngsild.agent.bg.http_upload import HttpUploadAgent
from pyngsild.agent.processor import build_sample_entity
from pyngsild.agent.stats import Stats

agent = HttpUploadAgent(process=build_sample_entity)
client = TestClient(agent.app)


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "pyngsild-0.1.2"}


def test_upload_multipart():

    file = pkg_resources.resource_stream(__name__, "data/room.csv")

    response = client.post(
        "/uploadfile/",
        files={
            "file": ("room.csv", file),
        },
    )
    assert response.status_code == 201
    assert agent.stats == Stats(2, 2, 2, 0, 0)
    assert agent.status.calls == 1
    assert agent.status.success == 1
