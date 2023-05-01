import pandas as pd
import numpy as np
import argparse


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-betta_csv', dest='betta_csv', type=str)
    arg_parser.add_argument('-stock_csv', dest='stock_csv', type=str)
    
    args = arg_parser.parse_args()
    
    betta_db = pd.read_csv(args.betta_csv)
    stock_db = pd.read_csv(args.stock_csv)
    
    base_stock = 'MIX'
    invest_horizont = 2024
    country_risk = 16.78
    rf = 8.35
    rm = 26.22
    result_columns = ['id', 'file', 'type', 'betta', 'rm', 'rf', 'country_risk', 'invest_horizont']
    result_stock_db = pd.DataFrame(columns=result_columns)
    for stock_index in stock_db.index:
        stock = stock_db.loc[stock_index, 'id']
        betta_index = betta_db[(betta_db.iloc[:,1]==stock) & (betta_db.iloc[:,2]==base_stock)].index[0]
        result_row = {}
        result_row['id'] = stock
        result_row['file'] = stock + '.csv'
        result_row['type'] = 'МСФО'
        result_row['betta'] = float(betta_db.loc[betta_index, betta_db.iloc[:,4].name].replace(',', '.'))
        result_row['rm'] = rm
        result_row['rf'] = rf
        result_row['country_risk'] = country_risk
        result_row['invest_horizont'] = invest_horizont
        result_row = pd.Series(data=result_row)
        result_stock_db = pd.concat([result_stock_db, result_row.to_frame().transpose()], ignore_index=True)
    
    
    result_stock_db.to_csv("../stock_data/new_stock_data.csv")
        
    