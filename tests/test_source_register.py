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

from pyngsild.source import Source
from pyngsild.source.moresources import SourceMicrosoftExcel


def test_register_source():
    class MySource(Source):
        pass

    Source.register_extension("test", MySource)
    srcklass, binary, kwargs = Source.registered_extensions["test"]
    assert srcklass == MySource
    assert not binary
    assert kwargs == {}


def test_register_source_with_args():
    class MySource(Source):
        pass

    Source.register_extension("test", MySource, key1="value1", key2="value2")
    srcklass, binary, kwargs = Source.registered_extensions["test"]
    assert srcklass == MySource
    assert not binary
    assert kwargs == {"key1": "value1", "key2": "value2"}


def test_unregister_source():
    test_register_source()
    assert Source.registered_extensions["test"] is not None
    Source.unregister_extension("test")
    assert "test" not in Source.registered_extensions


def test_register_source_then_use_it():
    Source.register_extension("xlsx", SourceMicrosoftExcel, binary=True)

    # xlsx
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    src = Source.from_file(filename)
    rows = [row for row in src]
    assert len(rows) == 4
    assert rows[0].provider == "user"
    assert rows[0].record == "SH1HDR1;;;"
    assert rows[1].record == "SH1HDR2;;;"
    assert rows[2].record == "data1;11;12;13"
    assert rows[3].record == "data2;14;15;16"

    # xlsx.gz
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx.gz")
    src = Source.from_file(filename)
    rows = [row for row in src]
    assert len(rows) == 4
    assert rows[0].provider == "user"
    assert rows[0].record == "SH1HDR1;;;"
    assert rows[1].record == "SH1HDR2;;;"
    assert rows[2].record == "data1;11;12;13"
    assert rows[3].record == "data2;14;15;16"


def test_register_source_with_args_then_use_it():
    filename = pkg_resources.resource_filename(__name__, "data/test.xlsx")
    Source.register_extension(
        "xlsx", SourceMicrosoftExcel, binary=True, sheetid=1, ignore=1
    )
    src = Source.from_file(filename)
    rows = [row for row in src]
    assert len(rows) == 3
    assert rows[0].provider == "user"
    assert rows[0].record == "SH2HDR2;;;"
    assert rows[1].record == "data1;21;22;23"
    assert rows[2].record == "data2;24;25;26"
