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
from fastapi import File, UploadFile
from typing import Callable, Any
from anyio import Lock
from pyngsild.source import Source, Row
from pyngsild.sink import Sink, SinkStdout
from . import ManagedDaemon

logger = logging.getLogger(__name__)


class HttpUploadAgent(ManagedDaemon):
    def __init__(
        self,
        sink: Sink = SinkStdout(),
        process: Callable[[Row], None] = lambda row: row.record,
    ):
        super().__init__(sink, process)

        @self.app.post("/uploadfile/", status_code=201)
        async def create_upload_file(file: UploadFile = File(...)):
            logger.info(file.filename)
            lock = Lock()
            async with lock:
                self.status.lastcalltime = datetime.now()
                self.status.calls += 1
            src = Source.from_file(file.filename, fp=file.file)
            await self.trigger(src)
            return {"filename": file.filename}
