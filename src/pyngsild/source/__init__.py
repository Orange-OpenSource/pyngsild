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
Source for NGSI Agents to collect from.

Sources MUST respect the following protocol :
Each Source Class is a generator hence MUST implement __iter__().
Some Sources MAY implement close() if needed to free resources.
"""

import glob
import logging
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from itertools import chain, islice
from os.path import basename
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import Any, List, Sequence

from pyngsild.utils.stream import stream_from
from pyngsild.constants import RowFormat

logger = logging.getLogger(__name__)

DEFAULT_PROVIDER = "user"


@dataclass(eq=True)
class Row:
    """
    A row is a data record delivered from a Source.

    A row is composed of the record (the data itself) and the provider (the name of the datasource provider).
    For example, the provider can be the full qualified named of a remote file located on a FTP Server.
    The record could be a simple string, a CSV-delimited line, a full JSON document.
    """

    record: Any
    provider: str = DEFAULT_PROVIDER


ROW_NOT_SET = Row(None, None)


class Source(Iterable[Row]):
    """
    A Source is a pull datasource : any datasource we can iterate on.

    The library provides many sources.
    One can code its own Source just by extending Source, and providing a new Row for each iteration.
    """

    registered_extensions = {}

    def __init__(self, rows: Sequence[Row]):
        self.rows = rows

    def __iter__(self):
        yield from self.rows

    def head(self, n: int = 2) -> List[Row]:
        """return a list built from the first n elements"""
        return [*islice(self, n)]

    def first(self) -> Row:
        """return the first element"""
        row: Row = None
        try:
            row = self.head(1)[0]
        except Exception:
            pass
        return row

    def skip_header(self, lines: int = 1):
        """return a new Source with first n lines skipped, default is to skip only the first line"""
        return Source(islice(self, lines, None))

    def limit(self, n: int = 10):
        """return a new Source limited to the first n elements"""
        iterator = iter(self)
        return Source((next(iterator) for _ in range(n)))

    @classmethod
    def from_stream(cls, stream: Iterable[Any], provider: str = "user", fmt = RowFormat.TEXT, **kwargs):
        """automatically create the Source from a stream"""
        return SourceStream(stream, provider, fmt, **kwargs)

    @classmethod
    def from_stdin(cls, provider: str = "user", **kwargs):
        """automatically create the Source from the standard input"""
        return SourceStream(sys.stdin, provider, **kwargs)

    @classmethod
    def from_file(
        cls,
        filename: str,  # str | PathLike
        fp: SpooledTemporaryFile = None,
        provider: str = "user",
        **kwargs
    ):
        from .moresources import SourceJson, SourceXml

        binary = False
        klass = None
        ext = None
        ext1 = None

        """automatically create the Source from a filename, figuring out the extension, handles text, json, xml and zip+gzip compression"""

        suffixes = [s[1:] for s in Path(filename).suffixes]  # suffixes w/o dot
        if suffixes:
            ext = suffixes[-1]  # last suffix
            ext1 = suffixes[0]  # first suffix

        if "*" in cls.registered_extensions:
            klass, binary, kwargs = cls.registered_extensions["*"]
        elif ext1 in cls.registered_extensions:  # TODO : look at the 1st extension !
            klass, binary, kwargs = cls.registered_extensions[ext1]

        stream, suffixes = stream_from(filename, fp, binary)
        ext = suffixes[-1]

        if klass:
            return klass(stream, **kwargs)

        if ext == "json":
            content = stream.read()
            return SourceJson(content, provider=basename(filename), **kwargs)
        if ext == "xml":
            content = stream.read()
            return SourceXml(content, provider=basename(filename), **kwargs)
        return SourceStream(stream, provider=basename(filename), **kwargs)

    @classmethod
    def from_files(cls, filenames: Sequence[str], provider: str = "user", **kwargs):
        sources = [Source.from_file(f) for f in filenames]
        return SourceMany(sources)

    @classmethod
    def from_glob(cls, pattern: str, provider: str = "user", **kwargs):
        sources = [Source.from_file(f) for f in glob.glob(pattern)]
        return SourceMany(sources)

    @classmethod
    def from_globs(cls, patterns: Sequence[str], provider: str = "user", **kwargs):
        filenames = chain.from_iterable([glob.glob(p) for p in patterns])
        sources = [Source.from_file(f) for f in filenames]
        return SourceMany(sources)

    @classmethod
    def register_extension(cls, ext: str, src, *, binary: bool = False, **kwargs):
        cls.registered_extensions[ext] = (src, binary, kwargs)

    @classmethod
    def unregister_extension(cls, ext: str):
        if cls.is_registered_extension(ext):
            del cls.registered_extensions[ext]

    @classmethod
    def is_registered_extension(cls, ext: str):
        return ext in cls.registered_extensions

    @classmethod
    def register(cls, src, *, binary: bool = False, **kwargs):
        cls.register_extension("*", src, binary, kwargs)

    @classmethod
    def unregister(cls):
        cls.unregister_extension("*")

    def reset(self):
        pass

    def close(self):
        pass


class SourceStream(Source):
    def __init__(
        self, stream: Iterable[Any], provider: str = "user", fmt: RowFormat | str = RowFormat.TEXT, ignore_header: bool = False
    ):
        if ignore_header:
            next(stream)
        self.stream = stream
        self.provider = provider
        self.fmt = fmt

    def __iter__(self):
        match self.fmt:
            case RowFormat.JSON:
                from pyngsild.source.moresources import SourceJson
                for payload in self.stream:
                    yield from SourceJson(payload, self.provider)
            case RowFormat.XML:
                from pyngsild.source.moresources import SourceXml
                for payload in self.stream:
                    yield from SourceXml(payload, self.provider)                    
            case RowFormat.TEXT | str():
                for line in self.stream:
                    yield Row(line.rstrip("\r\n"), self.provider)        
            case _:           
                for x in self.stream:
                    yield Row(x, self.provider)


    def reset(self):
        pass


class SourceStdin(SourceStream):
    def __init__(self, **kwargs):
        super().__init__(stream=sys.stdin, **kwargs)


class SourceSingle(SourceStream):

    """A SourceSingle is Source built from a Python single element.
    """

    def __init__(self, row: Any, provider: str = "user", fmt: RowFormat = RowFormat.TEXT, ignore_header: bool = False):
        super().__init__([row], provider, fmt, ignore_header)


class SourceMany(Source):
    def __init__(self, sources: Sequence[Source], provider: str = "user"):
        self.sources = sources
        self.provider = provider

    def __iter__(self):
        for src in self.sources:
            yield from src
