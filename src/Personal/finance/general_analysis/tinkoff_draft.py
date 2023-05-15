from tinkoff.invest import Client
from tinkoff.invest.services import MarketDataService
from tinkoff.invest.schemas import InstrumentIdType
import re

if __name__=="__main__":
    
    TOKEN = ''

    with Client(TOKEN) as client:
        #price = client.market_data.get_last_prices(instrument_id="KYG875721634")
        #print(client.users.get_accounts())
        #print(price)
        shares = client.instruments.shares()
        #"^tencent[a-z]*[1-9]*"
        share = list(filter(lambda share: re.search("^Dongfeng[a-z]*[1-9]*", share.name, re.IGNORECASE), shares.instruments))
        print(client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id="KYG875721634"))
        pass