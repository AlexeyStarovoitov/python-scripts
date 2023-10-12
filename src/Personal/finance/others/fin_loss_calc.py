import pandas as pd
import numpy as np
from enum import Enum

class Currency(Enum):
    RUB=1
    CNY=2
    HKD=3
    USD=4

class ColumnName(Enum):
    NAME=1
    VALUE=2
    CURRENCY=3
    LOSS=4
    LOSS_REL_TO_PORTFOLIO=5
    VALUE_O=6

portfolio = pd.Series([205367, 132074, 200025])
gain = pd.Series([-10305, 5845, 3993])
portfolio_o = sum(portfolio - gain)

currency_rates = [1, 12.592, 11.367, 90.025]
currency_names = [Currency.RUB, Currency.CNY, Currency.HKD, Currency.USD]
currency_data = dict(zip(currency_names, currency_rates))
currency_exchange = pd.DataFrame(data=currency_data, index=range(len(currency_names)))

assets_data = {ColumnName.NAME:pd.Series(["JD.com", "Yankuang", "GCL", "CSPC", "Construction Bank", "Anhui", "Bank of China","Shenhua", "Industrial Bank"]),
               ColumnName.VALUE: pd.Series([3044, 1560, 328, 2552, 890, 209, 283, 4660, 370]),
               ColumnName.CURRENCY: pd.Series([Currency.HKD, Currency.HKD, Currency.HKD,Currency.HKD,Currency.HKD,Currency.HKD,Currency.HKD,Currency.HKD,Currency.HKD]),
               ColumnName.LOSS: pd.Series([17.01, 17.219, 15.46, 15.05, 11.18, 15.56, 15.77, 9.96, 19.74])}

assets_data[ColumnName.LOSS_REL_TO_PORTFOLIO] = pd.Series([0]*len(assets_data[ColumnName.NAME]))
assets = pd.DataFrame(assets_data)

assets[ColumnName.VALUE] = pd.Series([assets.loc[i,ColumnName.VALUE]*currency_exchange[assets.loc[i,ColumnName.CURRENCY]].iloc[0] for i in assets.index])
assets[ColumnName.VALUE_O] = pd.Series([assets.loc[i,ColumnName.VALUE]/(1-assets.loc[i,ColumnName.LOSS]/100) for i in assets.index])
assets[ColumnName.LOSS_REL_TO_PORTFOLIO] = pd.Series([assets.loc[i,ColumnName.VALUE_O]/portfolio_o * assets.loc[i,ColumnName.LOSS] for i in assets.index])
assets.sort_values(by=ColumnName.LOSS_REL_TO_PORTFOLIO, ascending=False, inplace=True)
print(assets)





