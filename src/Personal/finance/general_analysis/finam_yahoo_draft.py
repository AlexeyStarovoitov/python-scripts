from finam_trade_api.client import Client
import yfinance as yf
import asyncio
import re

if __name__=="__main__":
    
    TOKEN = ''

    client = Client(TOKEN)
    shares = asyncio.run(client.securities.get_data())
    share = list(filter(lambda share: re.search("^Dongfeng[a-z]*[1-9]*", share.shortName, re.IGNORECASE), shares.data.securities))[0]
    tick = share.code.split(".")[0]
    Dongfeng = yf.Ticker(tick+".HK")
    print(Dongfeng.info["earnings"])
    pass