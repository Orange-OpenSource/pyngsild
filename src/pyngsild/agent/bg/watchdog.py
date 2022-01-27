#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import asyncio
import threading
import logging

from datetime import datetime
from typing import Callable
from watchgod import awatch
from watchgod.watcher import Change
from asyncio import Event
from pathlib import Path

from . import ManagedDaemon
from pyngsild.sink import Sink, SinkStdout
from pyngsild.source import Source, Row

logger = logging.getLogger(__name__)


class WatchDog(ManagedDaemon):
    """Watchdog looks a directory for new files."""

    def __init__(
        self,
        path: Path,
        *,
        sink: Sink = SinkStdout(),
        process: Callable[[Row], None] = lambda row: row.record,
    ):
        super().__init__(sink, process)
        self.path = path

    async def _aloop(self):
        self.stop_event = Event()
        async for changes in awatch(self.path, stop_event=self.stop_event):
            self.status.lastcalltime = datetime.now()
            self.status.calls += 1
            for mode, filename in changes:
                if mode != Change.added:
                    continue
                src = Source.from_file(filename)
                await self.trigger(src)

    def loop(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._aloop())

    def run(self):
        super().run()
        self._thread = threading.Thread(target=self.loop)
        self._thread.start()

    def close(self):
        self.stop_event.set()
        super().close()
        self._thread.join()
