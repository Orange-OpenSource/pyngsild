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

from typing import List

from pyngsild.source import Row, Source
from pyngsild.source.moresources import SourceXml


def test_source_xml():
    filename = pkg_resources.resource_filename(__name__, "data/books.xml")
    with open(filename) as f:
        content: str = f.read()
    src = SourceXml(content, path="Catalog.Book")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].record["Author"] == "Garghentini, Davide"
    assert rows[1].record["Author"] == "Garcia, Debra"


def test_source_xml_from_file():
    filename = pkg_resources.resource_filename(__name__, "data/books.xml")
    src = Source.from_file(filename, path="Catalog.Book")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "books.xml"
    assert rows[0].record["Genre"] == "Computer"
    assert rows[1].provider == "books.xml"
    assert rows[1].record["Genre"] == "Fantasy"


def test_source_xml_from_file_compressed():
    filename = pkg_resources.resource_filename(__name__, "data/books.xml.gz")
    src = Source.from_file(filename, path="Catalog.Book")
    rows: List[Row] = [x for x in src]
    assert len(rows) == 2
    assert rows[0].provider == "books.xml.gz"
    assert rows[0].record["Genre"] == "Computer"
    assert rows[1].provider == "books.xml.gz"
    assert rows[1].record["Genre"] == "Fantasy"
