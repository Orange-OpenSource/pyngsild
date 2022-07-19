#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

from ngsildclient import Entity, Client

# VEGAPULS 61 Device Sensor
vega61 = Entity(
    "DeviceModel",
    "liquidLevelSensor:Vega:Vegapuls61",
    ctx=[
        "https://github.com/smart-data-models/dataModel.Device/raw/aba14f18bb6e5f7ee1bd2f3b866d23c7ad630ad8/context.jsonld"
    ],
)
vega61.prop("brandName", "VEGA")
vega61.prop("modelName", "VEGAPULS 61")
vega61.prop("category", ["sensor"])
vega61.prop("controlledProperty", ["liquidLevel"])
vega61.prop("supportedUnits", "MTR")
vega61.prop(
    "seeAlso",
    "https://www.vega.com/en/products/product-catalog/level/radar/vegapuls-61",
)

# Bassens tide gauge station
bassens = Entity("Device", "tideGaugeSensor:SHOM:6119")
bassens.prop("name", "Bassens")
bassens.prop(
    "description",
    "The Bassens tide gauge station is part of the french tide gauge observation reference network (REFMAR)",
)
bassens.prop("shomId", 6119)
bassens.loc((44.904193, -0.537278))
bassens.prop("controlledProperty", "waterLevel")
bassens.prop("provider", "SHOM / GPM Bordeaux")
bassens.prop("address", "refmar@shom.fr")
bassens.rel("refDeviceModel", vega61.id)


def create_reference_entities():
    """Run once."""
    with Client() as client:
        client.upsert([bassens, vega61])


if __name__ == "__main__":
    create_reference_entities()
