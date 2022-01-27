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

from typing import Callable
from abc import ABCMeta, abstractmethod

from .stats import Stats
from ..source import Source, Row
from ..sink import Sink, SinkStdout
from ..sink.ngsi import SinkNgsi, SinkNgsiAsync
from ngsildclient import Entity

logger = logging.getLogger(__name__)


class BaseAgent(metaclass=ABCMeta):
    def __init__(
        self,
        sink: Sink = SinkStdout(),
        process: Callable = lambda row: row.record,
        side_effect: Callable = None,
    ):
        self.sink = sink
        self.process = process
        self.side_effect = side_effect
        self.stats = Stats()

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def close(self):
        pass  # free resources if needed


class Agent(BaseAgent):
    def __init__(
        self,
        src: Source,
        sink: Sink = SinkStdout(),
        process: Callable = lambda row: row.record,
        side_effect: Callable[[Row, Sink, Entity], int] = None,
    ):
        self.src = src
        super().__init__(sink, process, side_effect)

    def run(self):
        logger.info("start to acquire data")
        for row in self.src:
            logger.debug(row)
            try:
                logger.debug(f"{row.provider=}\t{row.record=}")
                self.stats.input += 1
                e: Entity = self.process(row)
                if e is None:
                    self.stats.filtered += 1
                    continue
                self.stats.processed += 1
                if isinstance(self.sink, (SinkNgsi, SinkNgsiAsync)):
                    self.sink.write(e)
                else:
                    msg = e.to_json() if isinstance(e, Entity) else e
                    self.sink.write(msg)
                self.stats.output += 1
                if self.side_effect:
                    side_entities = self.side_effect(row, self.sink, e)
                    self.stats.side_entities += side_entities
            except Exception as e:
                self.stats.error += 1
                logger.error(f"Cannot process record : {e}")
        self.close()
