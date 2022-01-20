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

from fastapi import requests
import pkg_resources

from typing import List

from pyngsild.source import Row, Source
from pyngsild.source.moresources import SourceJson


def test_source_json():
    content = r"""{
    "fruit": "Apple",
    "size": "Large",
    "color": "Red"
    }"""
    src = SourceJson(content)
    rows: List[Row] = [x for x in src]
    assert len(rows) == 1
    assert rows[0].provider == "user"
    assert rows[0].record["fruit"] == "Apple"


def test_source_json_array():
    content = r"""[ {"fruit": "Apple", "size": "Large", "color": "Red"},
    {"fruit": "Lime", "size": "Medium", "color": "Yellow"} ]"""
    src = SourceJson(content)
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "user"
    assert rows[0].record["fruit"] == "Apple"
    assert rows[1].provider == "user"
    assert rows[1].record["fruit"] == "Lime"


def test_source_json_path():
    content = r"""{"dataset": {"data": [ {"fruit": "Apple", "size": "Large", "color": "Red"},
    {"fruit": "Lime", "size": "Medium", "color": "Yellow"} ] } }"""
    src = SourceJson(content, path="dataset.data")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "user"
    assert rows[0].record["fruit"] == "Apple"
    assert rows[1].provider == "user"
    assert rows[1].record["fruit"] == "Lime"


def test_source_json_from_file():
    filename = pkg_resources.resource_filename(__name__, "data/users_sample.json")
    src = Source.from_file(filename, path="users")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 5
    assert rows[0].provider == "users_sample.json"
    assert rows[0].record["firstName"] == "Krish"
    assert rows[4].provider == "users_sample.json"
    assert rows[4].record["firstName"] == "jone"


def test_source_json_from_file_compressed():
    filename = pkg_resources.resource_filename(__name__, "data/users_sample.json.gz")
    src = Source.from_file(filename, path="users")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 5
    assert rows[0].provider == "users_sample.json.gz"
    assert rows[0].record["firstName"] == "Krish"
    assert rows[4].provider == "users_sample.json.gz"
    assert rows[4].record["firstName"] == "jone"
