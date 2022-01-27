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

from pyngsild.source import Row, Source, SourceStream, SourceStdin, SourceSingle
from pyngsild.source.moresources import SourceSample
from pyngsild.utils.stream import stream_from

def test_stream_from():
    zipname = pkg_resources.resource_filename(__name__, "data/test.txt.zip")
    src = Source.from_file(zipname)
    rows: list[Row] = [x for x in src]
    print(rows)
    assert rows == [Row("input5", "test.txt.zip"),
                    Row("input6", "test.txt.zip")]

def test_stream_from_2():
    zipfile = pkg_resources.resource_stream(__name__, "data/test.txt.zip")
    src = Source.from_file("test.txt.zip", fp=zipfile)
    rows: list[Row] = [x for x in src]
    print(rows)
    assert rows == [Row("input5", "test.txt.zip"),
                    Row("input6", "test.txt.zip")]