import requests
from ngsildclient import Entity, iso8601, Auto
from pyngsild.source import Row
from pyngsild.source.moresources import SourceJson
from pyngsild.sink import SinkStdout
from pyngsild.agent import Agent

COINGECKO_BASEURL = "https://api.coingecko.com/api/v3"
COINGECKO_COMPANIES_BTC_ENDPOINT = (
    f"{COINGECKO_BASEURL}/companies/public_treasury/bitcoin"
)


class SourceCoinGecko(SourceJson):
    def __init__(self):
        r = requests.get(COINGECKO_COMPANIES_BTC_ENDPOINT)
        super().__init__(r, path="companies", provider="CoinGecko API")


def build_entity(row: Row) -> Entity:
    record = row.record
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
sink = SinkStdout()
agent = Agent(src, sink, process=build_entity)
agent.run()
