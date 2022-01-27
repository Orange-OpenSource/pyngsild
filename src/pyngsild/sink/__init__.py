#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

"""
Sinks.

Sinks MUST respect the following protocol :
Each Sink Class MUST implement write().
Some Sinks MAY override close() if needed to free resources.

Other sinks such as SinkStdout or SinkFile are useful during the development stage and for unit testing.
"""


import gzip
import os

from abc import ABC, abstractmethod


class Sink(ABC):
    """
    Sink is an abstract class

    The library provides many sinks.
    One can code its own Sink just by extending Sink.
    """

    @abstractmethod
    def write(self, msg):
        raise NotImplementedError

    @property
    def status(self) -> dict:
        return {"state": "up"}

    def close(self):
        pass


class SinkException(Exception):
    pass


class SinkNull(Sink):
    """Do not write anything. For debugging purpose only."""

    def write(self, msg):
        pass


class SinkStdout(Sink):
    """Write to Standard Output"""

    def write(self, msg):
        print(msg)


class SinkFile(Sink):
    """Write to file"""

    def __init__(self, filename, append=False):
        """
        Parameters
        ----------
        filename : str
            The name of the output file
        """
        self.filename = filename
        try:
            self.file = open(self.filename, "a" if append else "w", encoding="utf8")
        except Exception as e:
            raise SinkException(f"cannot open file {self.filename} : {e}")

    def write(self, msg: str):
        try:
            self.file.write(f"{msg}{os.linesep}")
        except Exception as e:
            raise SinkException(f"cannot write to file {self.filename} : {e}")

    def close(self):
        try:
            self.file.close()
        except Exception as e:
            raise SinkException(f"cannot close file {self.filename} : {e}")


class SinkFileGzipped(SinkFile):
    """Write to gzipped file"""

    def __init__(self, filename):
        """
        Parameters
        ----------
        filename : str
            The name of the output file
        """
        self.filename = filename
        try:
            self.file = gzip.open(self.filename, "wt", encoding="utf8")
        except Exception as e:
            raise SinkException(f"cannot open file {self.filename} : {e}")
