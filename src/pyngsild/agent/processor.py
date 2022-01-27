#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from ..source import Row
from ngsildclient import Entity


def build_dummy_entity(row: Row) -> Entity:
    """
    Helper function to quickly build a dummy NGSI-LD compliant entity.
    """
    e = Entity("Dummy", "Dummy")
    e.prop("rawData", row.record)
    return e


def build_sample_entity(row: Row) -> Entity:
    """
    Helper function to build a NGSI-LD compliant entity for the NGSI walkthrough tutorial.

    Please have a look at : https://fiware-orion.readthedocs.io/en/master/user/walkthrough_apiv2/index.html#entity-creation
    Here we consider the input as a CSV line.
    """
    id, temperature, pressure = row.record.split(";")
    e = Entity("RoomTemperatureObserved", id)
    e.prop("temperature", float(temperature))
    e.prop("pressure", int(pressure))
    return e
