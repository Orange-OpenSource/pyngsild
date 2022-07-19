#!/usr/bin/env python3

# Software Name: pyngsild
# SPDX-FileCopyrightText: Copyright (c) 2021 Orange
# SPDX-License-Identifier: Apache 2.0
#
# This software is distributed under the Apache 2.0;
# see the NOTICE file for more details.
#
# Author: Fabien BATTELLO <fabien.battello@orange.com> et al.

import requests
import sys
from datetime import datetime, timedelta
from ngsildclient import *
from pyngsild import *

SHOM_ENDPOINT = "https://services.data.shom.fr/maregraphie/observation/json"
STATIONID_BASSENS = 6119


class SourceShom(SourceJson):
    def __init__(self, stationid: int):
        end = datetime.utcnow()
        start = end - timedelta(minutes=30)
        params = {
            "sources": 1,
            "dtStart": iso8601.from_datetime(start),
            "dtEnd": iso8601.from_datetime(end),
            "interval": 10,
        }
        r = requests.get(f"{SHOM_ENDPOINT}/{stationid}", params=params)
        super().__init__(r, path="data", provider="SHOM REFMAR API")


def build_entity(row: Row) -> Entity:
    record = row.record
    dt = datetime.strptime(record["timestamp"], "%Y/%m/%d %H:%M:%S")
    tidemeasure = Entity(
        "TideGaugeObserved", f"tideGaugeSensor:SHOM:6119:{iso8601.from_datetime(dt)}"
    )
    tidemeasure.obs()
    tidemeasure.prop("waterLevel", record["value"], unitcode="MTR", observedat=Auto)
    tidemeasure.rel(
        "refDevice", f"urn:ngsi-ld:Device:tideGaugeSensor:SHOM:{record['idstation']}"
    )
    tidemeasure.prop("dataProvider", row.provider)
    return tidemeasure


def main(stationid: int):
    src = SourceShom(stationid)
    sink = SinkNgsi()
    agent = Agent(src, sink, process=build_entity)
    agent.run()
    print(agent.stats)
    agent.close()


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 2:
        print(f"Usage : {argv[0]} <stationid>")
        sys.exit(1)
    stationid = int(argv[1])
    main(stationid)
