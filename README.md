# pyngsild

[![PyPI](https://img.shields.io/pypi/v/pyngsild.svg)](https://pypi.org/project/pyngsild/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

**pyngsild** is a Python data-centric framework whose goal is to ease and speed up the development of [NGSI-LD](https://fiware.github.io/specifications/ngsiv2/stable) agents.

By providing a clean and simple structure - with components organized as a dedicated NGSI-LD data pipeline - the framework allows the developer to avoid the plumbing and focus on the data.

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

**pyngsild** provides a level of abstraction to expose any datasource in a same way, whether :
- the agent **requests** data from a datasource *(i.e. reads a file, requests an API)*
- the agent **is triggered** by the datasource *(acts as a daemon listening to incoming data from the datasource)*

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

## License

[Apache 2.0](LICENSE)
