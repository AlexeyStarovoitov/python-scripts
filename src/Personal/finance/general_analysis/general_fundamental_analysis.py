import pandas as pd
import numpy as np
import argparse
import re
from enum import Enum
from openpyxl import workbook, worksheet
from openpyxl.reader import excel
from openpyxl.worksheet import dimensions


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
    D_E=15
    
class ColumnNameMapperColName(Enum):
    COLUMN_ENUM=1
    COLUMN_TEMPLATE=2
    COLUMN_ADDUCED_NAME=3

class ColumnNameOperation(Enum):
    COLUMN_MAP=1
    COLUMN_CONVERT=2

class ColumnNameMapper:
   
    def __init__(self):
        col_data = [ [ColumnName.NAME, ['^название[a-z]*[1-9]*', '^name[a-z]*[1-9]*'], 'name'],
                     [ColumnName.CAPITALIZATION, ['^капитализация[a-z]*[1-9]*'], 'cap'],
                     [ColumnName.P_E, ['^p/e[a-z]*[1-9]*'], 'P/E'],
                     [ColumnName.P_BV, ['^p/bv[a-z]*[1-9]*'], 'P/BV'],
                     [ColumnName.P_FCF, ['^p/fcf[a-z]*[1-9]*'], 'P/FCF'],
                     [ColumnName.P_S, ['^p/s[a-z]*[1-9]*'], 'P/S'],
                     [ColumnName.EV_EBIT, ['^ev/ebit[a-z]*[1-9]*'], 'EV/EBIT'],
                     [ColumnName.EV_S, ['^ev/s[a-z]*[1-9]*'], 'EV/S'],
                     [ColumnName.D_E, ['^debt/equity[a-z]*[1-9]*'], 'D/E'],
                     [ColumnName.ROE, ['^roe[a-z]*[1-9]*'], 'ROE'],
                     [ColumnName.COM_ANALYSIS_PE, [], 'P/E(comp)'],
                     [ColumnName.COM_ANALYSIS_P_FCF, [], 'P/FCF(comp)'],
                     [ColumnName.COM_ANALYSIS_EV_EBIT, [], 'EV/EBIT(comp)'],
                     [ColumnName.COM_ANALYSIS_P_S, [], 'P/S(comp)'],
                     [ColumnName.NET_ASSET_ANALYSIS, [], 'P/BV (comp)']
                     
        ]
        
        self._map_data = pd.DataFrame(data = col_data, columns = [ColumnNameMapperColName.COLUMN_ENUM, 
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
        column_entry = self._map_data[self._map_data[ColumnNameMapperColName.COLUMN_ENUM]==column_enum].iloc[0,:]
        if not column_entry.empty:
            return column_entry[ColumnNameMapperColName.COLUMN_ADDUCED_NAME]
        return None
    def enum2strconvert_columns(self, column_enums):
        converted_columns = [self.enum2strconvert(column) for column in column_enums]
        return converted_columns
        

class GeneralFundamentalAnalysis:
    p_bv = 1.5
    column_width = 15
    def __init__(self, csv_db):
        pd.set_option("display.precision", 3)
        np.set_printoptions(precision=3)
        self._db = pd.read_csv(csv_db)
        self._column_mapper = ColumnNameMapper()
        self._preprocess()
    def _map_column_general_operation(self, op_enum):
        db = self._db
        columns = list(db.columns)
        if op_enum == ColumnNameOperation.COLUMN_MAP:
            map_columns = self._column_mapper.map_columns(columns)
        elif op_enum == ColumnNameOperation.COLUMN_CONVERT:
            map_columns = self._column_mapper.enum2strconvert_columns(columns)
        column_rename_dict = dict(zip(columns, map_columns))
        db.rename(columns=column_rename_dict, inplace=True)
        
    def _map_columns(self):
       self._map_column_general_operation(ColumnNameOperation.COLUMN_MAP)
    def _enum2str_convert_columns(self):
        self._map_column_general_operation(ColumnNameOperation.COLUMN_CONVERT)
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
    def dump_to_excel(self, out_file_path):
        self._enum2str_convert_columns()
        writer = pd.ExcelWriter(path=out_file_path, engine='openpyxl')
        self._db.to_excel(excel_writer=writer, float_format="%.2f")
        writer.save()

        wb = excel.load_workbook(out_file_path)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            for row in ws.iter_rows(min_col=1, max_col=ws.max_column, max_row=1):
                for col in row:
                    ws.column_dimensions[col.column_letter] = dimensions.ColumnDimension(ws, index=col.column_letter, width=self.column_width)

        wb.save(out_file_path)
        
        
    def process(self):
        self._calculate_via_comparative_pe_analysis()
        self._calculate_via_comparative_ev_ebit()
        self._calculate_via_comparative_p_fcf_analysis()
        self._calculate_via_comparative_ps_analysis()
        self._calculate_via_net_assets()
        
        
if __name__=="__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-csv_db", dest="csv_db", type=str)
    arg_parser.add_argument("-out_file", dest="out_file", type=str)
    args = arg_parser.parse_args()
    gen_analysis = GeneralFundamentalAnalysis(args.csv_db)
    gen_analysis.process()
    gen_analysis.dump_to_excel(args.out_file)
    pass
    