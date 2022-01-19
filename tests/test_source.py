#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.
# SPDX-License-Identifier: Apache-2.0

import pkg_resources

from typing import List

from pyngsild.source import Row, Source, SourceStream, SourceStdin, SourceSingle
from pyngsild.source.moresources import SourceSample


def test_method_limit():
    src = SourceSample(count=5, delay=0)
    src = src.limit(2)
    assert isinstance(src, Source)
    lines = [x for x in src]
    assert len(lines) == 2


def test_method_head():
    src = SourceSample(count=5, delay=0)
    r = src.head(3)
    assert isinstance(r, list)
    assert len(r) == 3


def test_method_first():
    src = SourceSample(count=5, delay=0)
    row: Row = src.first()
    assert row.provider == "sample"


def test_method_skip_header():
    src = SourceSample(count=5, delay=0)
    src = src.skip_header(lines=2)
    lines = [x for x in src]
    assert len(lines) == 3


def test_source_list():
    src = SourceStream(["test1", "test2"])
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0] == Row("test1", "user")
    assert rows[1] == Row("test2", "user")


def test_source_single():
    src = SourceSingle("test1")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 1
    assert rows[0] == Row("test1", "user")


def test_source_stdin(mocker):
    mocker.patch('sys.stdin', {"input1", "input2"})
    src = SourceStdin()
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    # pytest capture input/output could mess the order
    assert Row("input1", "user") in rows
    assert Row("input2", "user") in rows


def test_source_sample():
    src = SourceSample(count=5, delay=0)
    rows: List[Row] = [x for x in src]
    assert len(rows) == 5
    assert rows[0] == Row("Room1;23;720", "sample")
    assert rows[1] == Row("Room2;21;711", "sample")
    assert "Room5;" in rows[4].record


def test_source_file(mocker):
    input_data = 'input1\ninput2\n'
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("builtins.open", mock_open)
    src = Source.from_file("test.txt")
    rows: List[Row] = [x for x in src]
    assert rows == [Row("input1", "test.txt"), Row("input2", "test.txt")]


def test_source_file_gz(mocker):
    input_data = 'input3\ninput4\n'
    mock_open = mocker.mock_open(read_data=input_data)
    mocker.patch("gzip.open", mock_open)
    src = Source.from_file("test.txt.gz")
    rows: List[Row] = [x for x in src]
    assert rows == [Row("input3", "test.txt.gz"), Row("input4", "test.txt.gz")]


def test_source_file_zip():
    zipname = pkg_resources.resource_filename(__name__, "data/test.txt.zip")
    src = Source.from_file(zipname)
    rows: List[Row] = [x for x in src]
    assert rows == [Row("input5", "test.txt.zip"),
                    Row("input6", "test.txt.zip")]
