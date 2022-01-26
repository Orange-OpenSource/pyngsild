import requests
from ngsildclient import Entity, iso8601, Auto
from pyngsild.source import Row
from pyngsild.source.moresources import SourceJson, SourceApi
from pyngsild.sink import SinkStdout
from pyngsild.agent import Agent

COINGECKO_API = "https://api.coingecko.com/api/v3"
COINGECKO_BTC_CAP_ENDPOINT = (
    f"{COINGECKO_API}/companies/public_treasury/bitcoin"
)


class SourceCoinGecko(SourceJson):
    def __init__(self):
        r = requests.get(COINGECKO_BTC_CAP_ENDPOINT)
        super().__init__(r, path="companies", provider="CoinGecko API")


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


src = SourceCoinGecko()

# As an alternative to inherit from the SourceJson class
# One could use SourceApi
# As in the line below
# src = SourceApi(lambda: requests.get(COINGECKO_BTC_CAP_ENDPOINT), path="companies", provider="CoinGecko API")

sink = SinkStdout()
agent = Agent(src, sink, process=build_entity)
agent.run()
