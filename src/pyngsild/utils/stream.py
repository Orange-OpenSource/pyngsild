#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import gzip
import logging
import urllib.request

from typing import Any
from zipfile import ZipFile
from io import StringIO, TextIOWrapper
from pathlib import Path
from tempfile import SpooledTemporaryFile


from ngsildclient.utils.url import isurl
from pyngsild.constants import FileMode

logger = logging.getLogger(__name__)


def stream_from(
    filename: str, fp: SpooledTemporaryFile = None, binary: bool = False
) -> tuple[TextIOWrapper, list[str]]:

    # if fp is set then filename is only here for metadata
    # SpooledTemporaryFile used for interoperability with FastAPI
    if isinstance(fp, SpooledTemporaryFile):  # here fp is not None
        fp = fp._file
    elif isurl(filename):
        fp = urllib.request.urlopen(filename)

    logger.debug(f"{filename=} {fp=}")
    try:
        suffixes = [s[1:] for s in Path(filename).suffixes]  # suffixes w/o dot
        ext = suffixes[-1]  # last suffix
        if ext == "gz":
            if binary:
                stream = gzip.open(filename if fp is None else fp, "rb")
            else:
                stream = gzip.open(
                    filename if fp is None else fp, "rt", encoding="utf-8"
                )
            return stream, suffixes[:-1]
        elif ext == "zip":
            zf = ZipFile(filename if fp is None else fp, "r")
            f = zf.namelist()[0]
            if binary:
                stream = zf.open(f, "r")
            else:
                stream = TextIOWrapper(zf.open(f, "r"), encoding="utf-8")
            return stream, suffixes
        else:
            if fp is None:
                if binary:
                    return open(filename, "rb"), suffixes
                else:
                    return open(filename, "rt", encoding="utf-8"), suffixes
            else:
                if binary:
                    return fp, suffixes
                else:
                    return TextIOWrapper(fp, encoding="utf-8"), suffixes
    except Exception as e:
        logger.error(f"Cannot open file {filename} : {e}")
