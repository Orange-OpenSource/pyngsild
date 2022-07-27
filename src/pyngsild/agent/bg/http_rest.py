#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import logging

from datetime import datetime
from pydantic import BaseModel
from typing import Callable, Any
from anyio import Lock
from pyngsild.constants import RowFormat
from pyngsild.source import SourceSingle, Row
from ngsildclient.model.entity import Entity
from pyngsild.sink import Sink, SinkStdout
from . import ManagedDaemon

logger = logging.getLogger(__name__)


class RoomObserved(BaseModel):
    room: int
    temperature: int
    pressure: float


def process(row: Row) -> Entity:
    room: RoomObserved = row.record
    e = Entity("RoomTemperatureObserved", room.room)
    e.prop("temperature", room.temperature)
    e.prop("pressure", room.pressure)
    return e


class HttpRestAgent(ManagedDaemon):
    def __init__(
        self,
        sink: Sink = SinkStdout(),
        process: Callable[[Row], None] = lambda row: row.record,
        endpoint: str = "/rooms/",
        mtype: type = RoomObserved
    ):
        super().__init__(sink, process)
        self.endpoint = endpoint
        self.mtype = mtype

        @self.app.post(self.endpoint, status_code=201)
        async def process(resource: self.mtype):
            lock = Lock()
            async with lock:
                self.status.lastcalltime = datetime.now()
                self.status.calls += 1
            src = SourceSingle(resource, fmt=RowFormat.UNDEFINED)
            await self.trigger(src)
            return resource
