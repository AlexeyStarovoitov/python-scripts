import pandas as pd
import numpy as np
from argparse import ArgumentParser
import re
import dcf_script as dcf

def pattern_match_is_found(pattern_vals, column):
	for pattern_val in pattern_vals:
		if re.search(pattern_val, column, re.IGNORECASE):
			return True
	return False

def parse_column_names(db_columns, pattern_dict):
	
	col_dict={}
	pattern_dict_item_list = list(pattern_dict.items())
	for column in db_columns:
		for pattern_key, pattern_vals in pattern_dict_item_list:
			if pattern_match_is_found(pattern_vals, column):
				col_dict[pattern_key] = column
				pattern_dict_item_list.remove((pattern_key, pattern_vals))
				break
		else:
			continue
	return col_dict
	
	

if __name__=='__main__':
	argparser = ArgumentParser()
	argparser.add_argument("-portfolio_db", dest="portfolio_db", type=str)
	args=argparser.parse_args()
	portfolio_db_file = args.portfolio_db
	portfolio_db = pd.read_csv(portfolio_db_file)

	result_columns = dict(stock_id=str, price_id=int, current_price=np.float64, calculated_price=np.float64, margin=np.float64)
	result_stock_pattern = dict(current_price=["current_price", "cur_price"],
								calculated_price=["calculated_price", "ev_price"], margin=["margin"])
	result_portfolio_db = pd.DataFrame(index = pd.RangeIndex(start=1, stop=1), columns=list(result_columns.keys()))
	'''
	for column_name, column_type in result_columns.items():
		new_col = pd.Series(data=np.zeros(len(1)), index=portfolio_db.index, dtype = column_type)
		result_portfolio_db.insert(loc = len(result_portfolio_db.columns), column=column_name, value=new_col)
	'''


	pattern_dict = dict(id=["id"], betta=["betta"], file=["file"], rm=["rm"], rf=["rf"], crp=["country_risk"], hrznt=["horizont"], type = ['type'])
	column_dict = parse_column_names(list(portfolio_db.columns), pattern_dict)
	for row_index in portfolio_db.index:
		cur_row = portfolio_db.loc[row_index, :].copy()
		dcf_clc = dcf.DCF_calc(csv_file='../stock_data/'+cur_row[column_dict['file']],\
							   betta = cur_row[column_dict['betta']], rf = cur_row[column_dict['rf']],\
							   rm = cur_row[column_dict['rm']], country_risk = cur_row[column_dict['crp']],\
							   invst_hrznt=int(cur_row[column_dict['hrznt']]), type = cur_row[column_dict['type']])
		result_stock_price = dcf_clc.calculate_fair_share_price()
		first_price = next(iter(result_stock_price))
		res_col_dict = parse_column_names(result_stock_price[first_price], result_stock_pattern)
		for price_id in result_stock_price:
			cur_result_stock_price = result_stock_price[price_id]
			result_row = {'stock_id':cur_row[column_dict['id']], 'price_id':price_id}
			for key in res_col_dict.keys():
				result_row[key] = cur_result_stock_price[res_col_dict[key]]
			result_row = pd.Series(data=result_row)
			result_portfolio_db = pd.concat([result_portfolio_db, result_row.to_frame().transpose()], ignore_index = True)

	new_index = list(range(1, len(result_portfolio_db) + 1))
	#result_portfolio_db.reindex(labels=new_index, index=new_index)
	result_portfolio_db.index = pd.RangeIndex(start = 1, stop = len(result_portfolio_db)+1, step = 1)
	portfolio_db_file_path = portfolio_db_file
	portfolio_db_file_path_splt = portfolio_db_file_path.split(".csv")
	new_portfolio_db_file_path = portfolio_db_file_path_splt[0]+ "dcf_analysis.html"
	result_portfolio_db.to_html(new_portfolio_db_file_path)
    	
	
	