#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from __future__ import annotations
from dataclasses import dataclass


@dataclass(eq=True)
class Stats:
    """
    Agent processing statistics
    """

    input: int = 0
    processed: int = 0
    output: int = 0
    filtered: int = 0
    error: int = 0
    side_entities: int = 0

    def __add__(self, o: Stats):
        return Stats(
            self.input + o.input,
            self.processed + o.processed,
            self.output + o.output,
            self.filtered + o.filtered,
            self.error + o.error,
            self.side_entities + o.side_entities,
        )

    def __iadd__(self, o: Stats):
        self.input += o.input
        self.processed += o.processed
        self.output += o.output
        self.filtered += o.filtered
        self.error += o.error
        self.side_entities += o.side_entities
        return self

    def zero(self):
        self.input = 0
        self.processed = 0
        self.output = 0
        self.filtered = 0
        self.error = 0
        self.side_entities = 0
        return self
