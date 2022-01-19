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

import pandas as pd

from pyngsild.source.moresources import SourceDataFrame


def test_source():
    # Sample from https://www.w3schools.com/python/pandas/pandas_dataframes.asp
    data = {"calories": [420, 380, 390], "duration": [50, 40, 45]}
    df = pd.DataFrame(data)
    src = SourceDataFrame(df)
    rows = [row for row in src]
    assert len(rows) == 3
    assert rows[0].provider == "DataFrame"
    assert rows[0].record.Index == 0
    assert rows[0].record.calories == 420
    assert rows[0].record.duration == 50
    assert rows[1].provider == "DataFrame"
    assert rows[1].record.Index == 1
    assert rows[1].record.calories == 380
    assert rows[1].record.duration == 40
    assert rows[2].provider == "DataFrame"
    assert rows[2].record.Index == 2
    assert rows[2].record.calories == 390
    assert rows[2].record.duration == 45
