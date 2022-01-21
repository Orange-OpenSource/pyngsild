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

from enum import Enum

class FileMode(Enum):
    BINARY = True
    TEXT = False
    
class RowFormat(Enum):
    TEXT = "text"
    JSON = "json"
    XML = "xml"
    