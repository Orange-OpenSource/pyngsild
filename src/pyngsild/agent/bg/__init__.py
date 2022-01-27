#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import threading
import anyio
import uvicorn
import logging
import time
import sys

from fastapi import FastAPI, File, UploadFile
from typing import Callable, Any
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from anyio import Lock
from uvicorn import server
from uvicorn.config import LoopSetupType

from pyngsild import __version__
from pyngsild.agent import BaseAgent, Agent
from pyngsild.source import Source, Row
from pyngsild.sink import Sink, SinkStdout

logger = logging.getLogger(__name__)


class State(Enum):
    PENDING = 0
    RUNNING = 1
    CLOSED = 2
    ERROR = 3


@dataclass
class Status:
    state: State = State.PENDING
    starttime: datetime = None
    lastcalltime: datetime = None
    calls: int = 0
    success: int = 0
    errors: int = 0


class Daemon(BaseAgent):
    def __init__(
        self,
        sink: Sink = SinkStdout(),
        process: Callable[[Row], Any] = lambda row: row.record,
    ):
        super().__init__(sink, process)
        self.status = Status()

    @classmethod
    def from_agent():
        pass

    async def trigger(
        self, src: Source
    ):  # a Daemon server will have to create a source then call this method
        logger.info(f"{src=}")
        try:
            agent = Agent(src, self.sink, self.process)
            agent.run()
            agent.close()
        except Exception as e:
            logger.error("Error while running agent", e)
            lock = Lock()
            async with lock:
                self.status.errors += 1
            return None
        lock = Lock()
        async with lock:
            self.status.success += 1
            self.stats += agent.stats
        return agent.stats


class ManagedDaemon(Daemon):
    def __init__(
        self, sink: Sink = SinkStdout(), process: Callable = lambda row: row.record
    ):
        super().__init__(sink, process)

        self.app = FastAPI()

        self.config = uvicorn.Config(
            app=self.app, host="localhost", port=8000, log_level="debug", loop="asyncio"
        )
        self.server = uvicorn.Server(config=self.config)
        # self.loop = None

        @self.app.on_event("startup")
        async def startup_event():
            logger.info("Start FastAPI HTTP server")

        @self.app.on_event("shutdown")
        def shutdown_event():
            logger.info("Shutdown FastAPI HTTP server")
            # self.loop.stop()

        @self.app.get("/status")
        async def status():
            return {"status": asdict(self.status), "sink": self.sink.status}

        @self.app.get("/version")
        async def version():
            return {"version": f"pyngsild-{__version__}"}

    def _loopwebadmin(self):
        if self.status.state == State.CLOSED:
            return
        try:
            # self.loop.run_until_complete(self.server.serve())
            self.server.run()
        except:
            logger.debug(sys.exc_info())
        while self.status.state != State.CLOSED:
            time.sleep(1)

    def run(self):
        self.status.starttime = datetime.now()
        self.status.state = State.RUNNING
        self.thread = threading.Thread(target=self._loopwebadmin)
        self.thread.start()

    async def aclose(self):
        logger.info("server => should_exit")
        self.server.should_exit = True
        # self.server.force_exit = True
        time.sleep(1)
        logger.info("state => CLOSED")
        self.status.state = State.CLOSED
        time.sleep(1)
        logger.info("await shutdown()")
        await self.server.shutdown()
        time.sleep(1)
        logger.info("join thread")
        self.thread.join()

    def close(self):
        anyio.run(self.aclose)
