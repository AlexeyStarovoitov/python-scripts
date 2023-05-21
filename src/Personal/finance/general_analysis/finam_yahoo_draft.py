from finam_trade_api.client import Client
import yfinance as yf
import asyncio
import re
import numpy as np
import pandas as pd
from general_fundamental_analysis import ColumnName, ColumnNameMapper, ColumnNameOperation
# unsuccessful stock screeners
'''
import pandas_datareader.data as web
import investiny
import tradingView
'''

class StockPriceScreener:
    def __init__(self, finam_token):
        self.finam_client = Client(finam_token)
        self._shares = asyncio.run(self.finam_client.securities.get_data())
        self._column_mapper = ColumnNameMapper()
       
    def _preprocess_stock_name(self, stock_name):
        stock_name = stock_name.strip("\'\"")
        stock_name_parts = list(stock_name.split())
        filter_func = lambda part: re.search("co.", part, re.IGNORECASE) == None and re.search("company", part, re.IGNORECASE)
        if filter_func(stock_name_parts[-1]):
            stock_name_parts.remove(stock_name_parts[-1])
        #stock_name_parts = filter(filter_func, stock_name_parts[])
        stock_name = ' '.join(stock_name_parts)
        return stock_name
    def _map_column_general_operation(self, op_enum):
        db = self._db
        columns = list(db.columns)
        if op_enum == ColumnNameOperation.COLUMN_MAP:
            map_columns = self._column_mapper.map_columns(columns)
        elif op_enum == ColumnNameOperation.COLUMN_CONVERT:
            map_columns = self._column_mapper.enum2strconvert_columns(columns)
        column_rename_dict = dict(zip(columns, map_columns))
        db.rename(columns=column_rename_dict, inplace=True)
    def _preprocces_db(self):
        self._map_column_general_operation(ColumnNameOperation.COLUMN_MAP)
        db = self._db
        db[ColumnName.PRICE] = pd.Series([0]*len(db),index=db.index, dtype=np.float32)
    def process(self, db_csv_path):
        self._db_csv_path = db_csv_path
        self._db = pd.read_csv(db_csv_path)
        self._preprocces_db()
        db = self._db
        
        for i in db.index:
            cur_entry = db.loc[i,:]
            stock_name = self._preprocess_stock_name(cur_entry.loc[ColumnName.NAME])
            search_pattern = f"^{stock_name}[a-z]*[0-9]*"
            filter_lambda = lambda share: re.search(search_pattern, share.shortName, re.IGNORECASE) and (re.search("^[0-9]*.XHKG", share.code, re.IGNORECASE) or re.search("^[0-9]{3,4}", share.code, re.IGNORECASE))
            share = list(filter(filter_lambda, self._shares.data.securities))
            if len(share) == 0:
                continue
            share = share[0]
            ticker = share.code.split(".")[0]
            if len(ticker) < 4:
                ticker = "0"*(4-len(ticker)) + ticker
            share_yahoo = yf.Ticker(ticker+".HK")
            db.loc[i,ColumnName.PRICE] = share_yahoo.info["currentPrice"]
        self._map_column_general_operation(ColumnNameOperation.COLUMN_CONVERT)
        self._db.to_csv(self._db_csv_path)
    
        



if __name__=="__main__":
    base_path = "C:\\Users\\Алексей\\python-scripts\\data\\"
    hk_data = pd.read_excel(base_path+"isinsehk.xlsx")
    hk_data.dropna(axis=0, inplace=True)
    
    
    data_sets = ["stocks_financemarker_china_finance.csv",
            "stocks_financemarker_china_it.csv",
            "stocks_financemarker_china_materials_energy.csv"
            ]
    screener = StockPriceScreener(finam_token)
    for data in data_sets:
        screener.process(base_path+data)

    
    
    '''
    finam_client = Client(finam_token)
    shares = asyncio.run(finam_client.securities.get_data())
    share = list(filter(lambda share: re.search("^Dongfeng[a-z]*[1-9]*", share.shortName, re.IGNORECASE), shares.data.securities))[0]
    tick = share.code.split(".")[0]
    Dongfeng = yf.Ticker(tick+".HK")
    print(Dongfeng.info["currentPrice"])
    '''
    pass
    