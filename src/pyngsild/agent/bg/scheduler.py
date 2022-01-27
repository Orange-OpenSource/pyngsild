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
import time
import schedule
import threading
import logging

from datetime import datetime
from typing import Callable
from dataclasses import dataclass
from enum import Enum

from . import ManagedDaemon, State
from .. import Agent

logger = logging.getLogger(__name__)

# TODO : add a ThreadPoolExecutor to deal with NGSI API requests


class UNIT(Enum):
    seconds = "s"
    minutes = "m"
    hours = "h"
    days = "d"


class Scheduler(ManagedDaemon):
    """Scheduler takes an agent and polls at periodic intervals."""

    def __init__(
        self,
        agent: Agent,
        interval: int = 1,
        unit: UNIT = UNIT.minutes,
        func: Callable = None,
    ):
        # take an already created agent and reschedule it
        # 1 - a func may be provided to create a new Source
        # 2 - or the source may have a reset() method
        # 3 - or the Source __init__() is called to reinit the Source
        super().__init__(agent.sink, agent.process)
        self.src = agent.src
        self.interval = interval
        self.unit = unit
        self.func = func

        logger.info("schedule job")
        if self.unit == UNIT.seconds:
            schedule.every(self.interval).seconds.do(self.job)
            self.tick = 1
        elif self.unit == UNIT.minutes:
            schedule.every(self.interval).minutes.do(self.job)
            self.tick = 4
        elif self.unit == UNIT.hours:
            schedule.every(self.interval).hours.do(self.job)
            self.tick = 32
        elif self.unit == UNIT.days:
            schedule.every(self.interval).days.do(self.job)
            self.tick = 128

    async def _ajob(self):
        logger.info(f"start new job at {datetime.now()}")
        self.status.lastcalltime = datetime.now()
        self.status.calls += 1

        # "reinit" the Source
        if self.func is not None:
            self.src = (
                self.func()
            )  # get a new Source if such a method has been provided
        else:
            src = self.src
            if hasattr(src, "reset"):
                src.reset()
            else:
                src.__init__()

        await self.trigger(src)

    def job(self):
        anyio.run(self._ajob)

    def _loop(self):
        while self.status.state != State.CLOSED:
            logger.debug("tick")
            schedule.run_pending()
            time.sleep(self.tick)

    def run(self):
        super().run()
        self.job()

        thread = threading.Thread(target=self._loop)
        thread.start()

    def close(self):
        schedule.cancel_job(self.job)
        super().close()
