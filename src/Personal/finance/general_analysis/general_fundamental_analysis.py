import pandas as pd
import numpy as np
import argparse
import re
from enum import Enum

class ColumnName(Enum):
    NAME=1
    CAPITALIZATION=2
    P_E=3
    P_BV=4
    P_S=14
    P_FCF=5
    EV_EBIT=6
    EV_S=7
    ROE=8
    COM_ANALYSIS_PE=9
    COM_ANALYSIS_P_FCF=10
    COM_ANALYSIS_EV_EBIT=11
    COM_ANALYSIS_P_S=12
    NET_ASSET_ANALYSIS=13
    
class ColumnNameMapperColName(Enum):
    COLUMN_ENUM=1
    COLUMN_TEMPLATE=2
    COLUMN_ADDUCED_NAME=3

class ColumnNameMapper:
   
    def __init__(self):
        col_data = [ [ColumnName.NAME, ['^название[a-z]*[1-9]*', '^name[a-z]*[1-9]*'], 'name'],
                     [ColumnName.CAPITALIZATION, ['^капитализация[a-z]*[1-9]*'], 'capitalization'],
                     [ColumnName.P_E, ['^p/e[a-z]*[1-9]*'], 'p_e'],
                     [ColumnName.P_BV, ['^p/bv[a-z]*[1-9]*'], 'p_bv'],
                     [ColumnName.P_FCF, ['^p/fcf[a-z]*[1-9]*'], 'p_fcf'],
                     [ColumnName.P_S, ['^p/s[a-z]*[1-9]*'], 'p_s'],
                     [ColumnName.EV_EBIT, ['^ev/ebit[a-z]*[1-9]*'], 'ev_ebit'],
                     [ColumnName.EV_S, ['^ev/s[a-z]*[1-9]*'], 'ev_s'],
                     [ColumnName.ROE, ['^roe[a-z]*[1-9]*'], 'roe'],
                     [ColumnName.COM_ANALYSIS_PE, [], 'comp_analysis_pe'],
                     [ColumnName.COM_ANALYSIS_P_FCF, [], 'comp_analysis_p_fcf'],
                     [ColumnName.COM_ANALYSIS_EV_EBIT, [], 'comp_analysis_ev_ebit'],
                     [ColumnName.COM_ANALYSIS_P_S, [], 'comp_analysis_ps'],
                     [ColumnName.NET_ASSET_ANALYSIS, [], 'net_asset_analysis']
                     
        ]
        
        self._map_data = pd.DataFrame(data = np.array(col_data), columns = [ColumnNameMapperColName.COLUMN_ENUM, 
                                                                            ColumnNameMapperColName.COLUMN_TEMPLATE, 
                                                                            ColumnNameMapperColName.COLUMN_ADDUCED_NAME])
    @staticmethod
    def _check_template_match(col_name, tem_list):
        for temp in tem_list:
            if re.search(temp, col_name, re.IGNORECASE):
                return True
        else:
            return False
    def map_column(self, col_name):
        for i in self._map_data.index:
            cur_name = self._map_data.loc[i, :]
            if ColumnNameMapper._check_template_match(col_name, cur_name[ColumnNameMapperColName.COLUMN_TEMPLATE]):
                return cur_name[ColumnNameMapperColName.COLUMN_ENUM]
        else:
            return None
    def map_columns(self, columns):
        map_columns = [self.map_column(column) for column in columns]
        return map_columns
    def enum2strconvert(self, column_enum):
        column_entry = self._map_data[self._map_data[ColumnNameMapperColName.COLUMN_ENUM]==column_enum]
        if column_entry:
            return column_entry[ColumnNameMapperColName.COLUMN_ADDUCED_NAME]
        return None
        

class GeneralFundamentalAnalysis:
    p_bv = 1.5
    def __init__(self, csv_db, out_file_path=None):
        self._db = pd.read_csv(csv_db)
        self._column_mapper = ColumnNameMapper()
        self._out_file = out_file_path
        self._preprocess()
    def _map_columns(self):
        db = self._db
        #rename columns
        columns = list(db.columns)
        map_columns = self._column_mapper.map_columns(columns)
        column_rename_dict = dict(zip(columns, map_columns))
        db.rename(columns=column_rename_dict)
    def _preprocess(self):
        self._map_columns()
        db = self._db
        #add series
        result_columns = [ColumnName.COM_ANALYSIS_PE, ColumnName.COM_ANALYSIS_EV_EBIT, 
                          ColumnName.COM_ANALYSIS_P_FCF, ColumnName.COM_ANALYSIS_P_S,
                          ColumnName.NET_ASSET_ANALYSIS]
        for res_column in result_columns:
            db[res_column] = pd.Series([0]*len(db),index=db.index, dtype=np.float32)
        
    @staticmethod
    def _map_proccessed_db(db, pr_db, proccess_column_name):
        for i, name in zip(pr_db[ColumnName.NAME].index, pr_db[ColumnName.NAME].to_numpy()):
            entry_index = db[ColumnName.NAME][db[ColumnName.NAME]==name].index[0]
            db.loc[entry_index, proccess_column_name] = pr_db.loc[i, proccess_column_name]
    
    def _calculate_via_general_analysis(self, parameter_column_name, result_column_name):
        db = self._db
        db_pr = db[db[parameter_column_name] > 0]
        means = db_pr.mean()
        db_pr[result_column_name] = (means[parameter_column_name]-db_pr[parameter_column_name])/means[parameter_column_name]*100
        GeneralFundamentalAnalysis._map_proccessed_db(db, db_pr, result_column_name)
    def _calculate_via_comparative_pe_analysis(self):
        self._calculate_via_general_analysis(ColumnName.P_E, ColumnName.COM_ANALYSIS_PE)
        '''
        db_pe= db_pe[(db_pe[ColumnName.P_E] > 0) & 
                (db_pe[ColumnName.P_E] < means[ColumnName.P_E]) & 
                (db_pe[ColumnName.COM_ANALYSIS_EV_EBIT] > 0) &
                (db_pe[ColumnName.COM_ANALYSIS_EV_EBIT] < means[ColumnName.COM_ANALYSIS_EV_EBIT]) & 
                (db_pe[ColumnName.COM_ANALYSIS_EV_EBIT] < db_pe[ColumnName.P_E])] #& 
                #(db_pe[ColumnName.ROE] > means[ColumnName.ROE])]
        '''
    def _calculate_via_comparative_p_fcf_analysis(self):
        self._calculate_via_general_analysis(ColumnName.P_FCF, ColumnName.COM_ANALYSIS_P_FCF)
    def _calculate_via_comparative_ps_analysis(self):
        self._calculate_via_general_analysis(ColumnName.P_S, ColumnName.COM_ANALYSIS_P_S)
    def _calculate_via_comparative_ev_ebit(self):
        db = self._db
        db_pr = db[db[ColumnName.EV_EBIT] > 0]
        s = db_pr[ColumnName.CAPITALIZATION]/db_pr[ColumnName.P_S]
        ev = db[ColumnName.EV_S]*s
        ebit = ev/db[ColumnName.EV_EBIT]
        debt = ev - db_pr[ColumnName.CAPITALIZATION]
        means = db_pr.mean()
        fair_price =  means[ColumnName.EV_EBIT]*ebit-debt
        db_pr[ColumnName.COM_ANALYSIS_EV_EBIT] = (fair_price-db_pr[ColumnName.CAPITALIZATION])/fair_price*100
        GeneralFundamentalAnalysis._map_proccessed_db(db, db_pr, ColumnName.COM_ANALYSIS_EV_EBIT)
    def _calculate_via_net_assets(self):
        db = self._db
        db_pr = db[db[ColumnName.P_BV] > 0]
        db_pr[ColumnName.NET_ASSET_ANALYSIS] = (self.p_bv-db_pr[ColumnName.P_BV])/self.p_bv*100
        GeneralFundamentalAnalysis._map_proccessed_db(db, db_pr, ColumnName.NET_ASSET_ANALYSIS)
    def process(self):
        self._calculate_via_comparative_pe_analysis()
        self._calculate_via_comparative_ev_ebit()
        self._calculate_via_comparative_p_fcf_analysis()
        self._calculate_via_comparative_ps_analysis()
        self._calculate_via_net_assets()
        
        if self._out_file:
            self._db.to_excel(self._out_file)
        else:
            print(f"Results:\n{self._db}")
        
if __name__=="__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-csv_db", dest="csv_db", type=str)
    arg_parser.add_argument("-out_file", dest="out_file", type=str)
    args = arg_parser.parse_args()
    gen_analysis = GeneralFundamentalAnalysis(args.csv_db, args.out_file)
    gen_analysis.process()
    