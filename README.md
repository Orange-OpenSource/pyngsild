# pyngsild

[![PyPI](https://img.shields.io/pypi/v/pyngsild.svg)](https://pypi.org/project/pyngsild/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

**pyngsild** is a Python data-centric framework whose goal is to ease and speed up the development of [NGSI-LD](https://fiware.github.io/specifications/ngsiv2/stable) agents.

By providing a clean and simple structure - with components organized as a NGSI-LD data pipeline - the framework allows the developer to avoid the plumbing and focus on the data.

## Key Features

- Agents that rely on the pyngsild framework all share a common structure
- Many DataSources included
- Statistics
- Monitoring *(for background agents)*
- Error handling
- Logging
- Well-tested components
- Provide primitives to build NGSI-LD compliant entities *(thanks to the [ngsildclient](https://pypi.org/project/ngsildclient/) library)*

## Air Pollutant HTTP Demo

How to create an HTTP NGSI-LD Agent which is uploaded each day with a CSV file.

## How it works

### DataSources

What most differentiates an agent from another is the datasource.

Not only the nature of the data differs but also :
- the data representation : text, json, ...
- the way data are accessed : read from a file, received through the network, ...

**pyngsild** provides a level of abstraction to expose any datasource in a same way, whether :
- the agent **consumes** a datasource *(i.e. reads a file, requests an API)*
- the agent **is triggered** by the datasource *(acts as a daemon listening to incoming data pushed by the datasource)*

The framework includes many Sources and Daemon Agents allowing to face different use cases.

### The pipeline

A NGSI-LD Agent typically :
- collects data from a datasource
- builds "normalized" NGSI-LD entities *according to a NGSI-LD domain-specific DataModel*
- eventually feeds the Context Broker

The framework allows to create an **Agent** by providing a **Source**, a **Sink** and a **processor** function.

The Source collects data from the datasource and is iterable.

When the Agent runs, it iterates over the Source to collect Rows.

The processor function takes a **Row** and builds a NGSI-LD **Entity** from it.

Eventually the Entity is send to the **Sink** which is in production mode the **Context Broker**.

<pre>
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                                                                                   |
|      +--------------+                                       +--------------+      |
|      |              |     Row                    Entity     |              |      |
|      |    Source    |-------------> process() ------------->|     Sink     |      |
|      |              |                                       |              |      |
|      +--------------+                                       +--------------+      |
|                                                                                   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
                                        Agent    
</pre>

## Where to get it
The source code is currently hosted on GitHub at :
https://github.com/Orange-OpenSource/pyngsild

Binary installer for the latest released version is available at the [Python
package index](https://pypi.org/project/pyngsild).

```sh
pip install pyngsild
```

## Installation

**pyngsild** requires Python 3.10+.

One should use a virtual environment. For example with pyenv.

```sh
mkdir myfiwareproject && cd myfiwareproject
pyenv virtualenv 3.10.1 myfiwareproject
pyenv local
pip install pyngsild
```

## Getting started

### Create a Source

Before developing our first agent it's important to have a clear understanding of how a Source works.

As datasources have very little in common, the only assumption made by the framework is : a Source is iterable.
In fact a Source is backed by a Python generator.

Many generic Sources are provided by the framework and it's easy to create a new one.

For example let's create a Source that collects data about companies bitcoin holdings thanks to the CoinGecko API.

```python
import requests

from pyngsild import *

COINGECKO_API = "https://api.coingecko.com/api/v3"
COINGECKO_BTC_CAP_ENDPOINT = f"{COINGECKO_API}/companies/public_treasury/bitcoin"

src = SourceApi(lambda: requests.get(COINGECKO_BTC_CAP_ENDPOINT), path="companies", provider="CoinGecko API")
```

Have a look [here](coingecko_btc_cap_sample.json) for a sample API result.

For the sake of experiment one could iterate over the Source using a for-loop to obtain Rows.

A Row is a dataclass composed of two attributes : record and provider
- record: Any = the raw incoming data
- provider: str = a label indicating the data provider

In this example a Row looks like this :

```json
Row(record={'name': 'MicroStrategy Inc.', 'symbol': 'NASDAQ:MSTR', 'country': 'US', 'total_holdings': 121044, 'total_entry_value_usd': 3574400000, 'total_current_value_usd': 4652725661, 'percentage_of_total_supply': 0.576}, provider='CoinGecko API')
```

### Provide a processor function

You have to provide the framework with a **processor** function, that will be used to transform a Row into a NGSI-LD compliant entity.

```python
from ngsildclient import *

def build_entity(row: Row) -> Entity:
    record: dict = row.record
    market, symbol = [x.strip() for x in record["symbol"].split(":")]
    e = Entity("BitcoinCapitalization", f"{market}:{symbol}:{iso8601.utcnow()}")
    e.obs()
    e.prop("dataProvider", row.provider)
    e.prop("companyName", record["name"])
    e.prop("stockMarket", market)
    e.prop("stockSymbol", symbol)
    e.prop("country", record["country"])
    e.prop("totalHoldings", record["total_holdings"], unitcode="BTC", observedat=Auto)
    e.prop("totalValue", record["total_current_value_usd"], unitcode="USD", observedat=Auto)
    return e
```

Please find [here](company_entity_sample.json) a sample NGSI-LD Entity built with this function.

### Run our first Agent

Let's create the Sink and make all parts work together.

```python
# replace by SinkStdout() if you don't have a Context Broker
sink = SinkNgsi()

agent = Agent(src, sink, process=build_entity)

agent.run()

# we can display statistics
print(agent.stats) # input=27, processed=27, output=27, filtered=0, error=0, side_entities=0

agent.close()
```

We're done !

27 entities *(at the time of writing)* should have been created in the Context Broker.

## License

[Apache 2.0](LICENSE)

## Roadmap

- Add documentation