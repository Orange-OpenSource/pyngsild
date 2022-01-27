#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import anyio
import asyncio
import threading
import logging

from typing import Callable
from datetime import datetime

from . import ManagedDaemon
from pyngsild.sink import Sink, SinkStdout
from pyngsild.source import SourceSingle, Row

logger = logging.getLogger(__name__)

EOT = b"PYNGSILD|EOT\n"


class UdpServer(ManagedDaemon):
    """UdpServer allows receiving UDP datagrams.

    A typical use case is to gather NMEA data from an AIS-receiver.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 10110,
        *,
        sink: Sink = SinkStdout(),
        process: Callable[[Row], None] = lambda row: row.record,
    ):
        super().__init__(sink, process)
        self.host = host
        self.port = port

    async def _aloop(self):
        print(f"{self.port=}")
        async with await anyio.create_udp_socket(
            local_host=self.host, local_port=self.port
        ) as udp:
            logger.info(f"Connected : {self.host=} {self.port=}")
            async for packet, (host, port) in udp:
                if packet == EOT:
                    return
                self.status.lastcalltime = datetime.now()
                self.status.calls += 1
                src = SourceSingle(packet.decode("utf-8"), provider="udp")
                await self.trigger(src)

    def loop(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self._aloop())

    def run(self):
        super().run()
        self._thread = threading.Thread(target=self.loop)
        self._thread.start()

    async def send_in_band_EOT(self):
        async with await anyio.create_connected_udp_socket(
            remote_host=self.host, remote_port=self.port
        ) as udp:
            await udp.send(EOT)

    def close(self):
        super().close()
        anyio.run(self.send_in_band_EOT)
        self._thread.join()
