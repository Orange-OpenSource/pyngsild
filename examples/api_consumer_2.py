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
from pyngsild.source.moresources import SourceJson
from pyngsild.agent import Agent

TZ = "Europe/Paris"
TIMEIO_BASEURL = "https://www.timeapi.io/api"
TIMEIO_CURTIME_ENDPOINT = f"{TIMEIO_BASEURL}/Time/current/zone?timeZone={TZ}"


def get_time():
    return requests.get(TIMEIO_CURTIME_ENDPOINT)


src = SourceJson(get_time)
agent = Agent(src)
agent.run()
