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
from os import PathLike

import sys
import time
import random
import json
import operator
import xmltodict
import pandas as pd
import openpyxl
import logging

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from _typeshed import SupportsRead

from functools import reduce
from pathlib import Path

from pyngsild.constants import SupportsJson
from . import Source, Row

logger = logging.getLogger(__name__)


class SourceSample(Source):

    """
    SourceSample implements the Source from the NGSI Walkthrough tutorial.

    Please have a look at :
    https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creationhttps://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation

    First two records are those of the tutorial.
    Following records are randomized.
    """

    def __init__(self, count: int = 5, delay: float = 1.0):
        self.count = count if count > 0 else sys.maxsize
        self.delay = delay

    def __iter__(self):
        i: int = 0
        if self.count >= 1:  # 1st element is fixed
            yield Row("Room1;23;720", "sample")
            i += 1
            time.sleep(self.delay)
        if self.count >= 2:  # 2nd element is fixed
            yield Row("Room2;21;711", "sample")
            i += 1
            time.sleep(self.delay)
        # next elements are randomized
        while i < self.count:
            yield Row(
                f"Room{i%9+1};{round(random.uniform(-10,50), 1)};{random.randint(700,1000)}",
                "sample",
            )
            i += 1
            time.sleep(self.delay)


class SourceDict(Source):
    """Read JSON formatted data from JSON object"""

    def __init__(self, payload: dict, provider: str = "user", path: str = None):
        self.payload = payload
        self.provider = provider
        self.path = path

    def __iter__(self):
        obj = self._attr(self.path) if self.path else self.payload
        if isinstance(obj, list):
            for j in obj:
                yield Row(j, self.provider)
        else:
            yield Row(obj, self.provider)

    def _attr(self, element: str):
        return reduce(operator.getitem, element.split("."), self.payload)


class SourceJson(SourceDict):
    """Read JSON formatted data from JSON object"""

    def __init__(
        self, content: str | SupportsJson, provider: str = "user", path: str = None
    ):
        if hasattr(content, "json"):  # useful for requests.Response
            payload = content.json()
        else:
            payload = json.loads(content)
        super().__init__(payload, provider, path)


class SourceApi(SourceJson):
    """Read JSON data from the result of a function.

    The function result should be compatible with a requests.Response : provide a json() method
    """

    def __init__(
        self,
        f_call_api: Callable[..., SupportsJson],
        provider: str = "user",
        path: str = None,
    ):
        response: SupportsJson = f_call_api()
        super().__init__(response, provider, path)


class SourceXml(SourceDict):
    """Read JSON formatted data from XML content"""

    def __init__(
        self,
        content: str | SupportsRead | PathLike,
        provider: str = "user",
        path: str = None,
    ):
        payload = xmltodict.parse(content)
        super().__init__(payload, provider, path)


class SourceMicrosoftExcel(Source):
    def __init__(
        self,
        filename,  # path-like or file-like
        sheetid: int = 0,
        sheetname: str = None,
        ignore: int = 0,
    ):
        logger.debug(f"{filename=}")
        wb = openpyxl.load_workbook(filename, data_only=True)
        ws = wb[sheetname] if sheetname else wb.worksheets[sheetid]
        self.rows = ws.rows
        if isinstance(filename, str):  # TODO : deal with file
            self.provider = Path(filename).name
        else:
            self.provider = "user"
        for _ in range(ignore):  # skip lines
            next(self.rows)

    def __iter__(self):
        for row in self.rows:
            record = ";".join([str(cell.value) if cell.value else "" for cell in row])
            logger.debug(f"{self.provider=}{record=}")
            yield Row(record, self.provider)


class SourceFunc(Source):
    """A SourceFunc receives its incoming data through a given user function

    The user function is passed as an argument at init time.
    In some cases it may avoid subclassing the Source class.
    """

    def __init__(self, func: Callable[..., List], provider: str = "api"):
        self.func = func
        self.provider = provider

    def __iter__(self):
        for response in self.func():
            yield Row(response, self.provider)


class SourceDataFrame(Source):
    """A SourceDataFrame takes its incoming data from a pandas DataFrame"""

    def __init__(self, df: pd.DataFrame, provider: str = "DataFrame"):
        self.df = df
        self.provider = provider

    def __iter__(self):
        for row in self.df.itertuples():
            yield Row(row, self.provider)
