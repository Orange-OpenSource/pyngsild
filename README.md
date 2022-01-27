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

## How it works

### DataSources

What most differentiates an agent from another is the datasource.

Not only the nature of the data differs but also :
- the data representation : text, json, ...
- the way data are accessed : read from a file, received through the network, ...

**pyngsild** provides a level of abstraction in order to expose any datasource in a same way, whether :
- the agent **consumes** a datasource *(i.e. reads a file, requests an API)*
- the agent **is triggered** by the datasource *(acts as a daemon listening to incoming data pushed by the datasource)*

As datasources have very little in common, the only assumption made by the framework is : a **pyngsild** Source is iterable.

*For illustrative purposes an element accessed from a Source could be a line from a CSV file, an item from a JSON array, or a row from a Pandas dataframe.*

Many generic Sources are provided by the framework and it's easy to create new ones.

### The pipeline

A NGSI-LD Agent typically :
- collects data from a datasource
- builds "normalized" NGSI-LD entities *(according to a domain-specific DataModel)*
- eventually feeds the Context Broker

The framework allows to create an **Agent** by providing a **Source**, a **Sink** and a **processor** function.

The Source collects data from the datasource.

When the Agent runs, it iterates over the Source to collect Rows.

The processor function takes a **Row** and builds a NGSI-LD **Entity** from it.

A Row is an object composed of two attributes : record and provider
- record: Any = the raw incoming data
- provider: str = a label indicating the data provider

Eventually the Entity is sent to the **Sink** which is in production mode the **Context Broker**.

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
pyenv virtualenv 3.10.2 myfiwareproject
pyenv local
pip install pyngsild
```

## Getting started

### Create a Source

For example let's create a Source that collects data about companies bitcoin holdings thanks to the CoinGecko API.

```python
import requests
from pyngsild import *
from ngsildclient import *

COINGECKO_BTC_CAP_ENDPOINT = "https://api.coingecko.com/api/v3/companies/public_treasury/bitcoin"

src = SourceApi(lambda: requests.get(COINGECKO_BTC_CAP_ENDPOINT), path="companies", provider="CoinGecko API")
```

Have a look [here](coingecko_btc_cap_sample.json) for a sample API result.

### Provide a processor function

You have to provide the framework with a **processor** function, that will be used to transform a Row into a NGSI-LD compliant entity.

```python
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

Have a look [here](company_entity_sample.json) for a sample NGSI-LD Entity built with this function.

### Run the Agent

Let's create the Sink, the Agent and make all parts work together.

```python
sink = SinkNgsi() # replace by SinkStdout() if you don't have a Context Broker
agent = Agent(src, sink, process=build_entity)
agent.run()
print(agent.stats) # input=27, processed=27, output=27, filtered=0, error=0, side_entities=0
agent.close()
```

We're done !

The Context Broker should have created a set of entities *(27 at the time of writing)*.

## License

[Apache 2.0](LICENSE)
