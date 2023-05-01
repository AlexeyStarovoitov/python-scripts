import pandas as pd
import numpy as np
import argparse


class GeneralFundamentalAnalysis:
    multi_cols_names = ['Название', 'P/E', 'EV/EBIT', 'P/BV', 'P/S', 'P/FCF', 'ROE']
    tol = 0.05
    p_bv = 1.5
    def __init__(self, csv_db, out_file_path=None):
        self._db = pd.read_csv(csv_db)
        self._out = open(out_file_path, "w") if out_file_path else None
        if self._out:
            self._out.write(f'Initial data:\n{self._db}\n\n')
    def _preprocess(self):
        cols = list(map(lambda i: i, filter(lambda u: u not in self.multi_cols_names, self._db.columns)))
        self._db.drop(cols, inplace=True, axis=1)
    def _calculate_via_comparative_pe_analysis(self):
        db_pe = self._db.copy(deep=True)
        db_pe.drop(['P/BV', 'P/S'], inplace=True, axis=1)
        db_pe = db_pe[db_pe['P/E'] > 0]
        means = db_pe.mean()
        db_pe['yield(comp_analysis_p_e)'] = (means['P/E']-db_pe['P/E'])/means['P/E']*100
        db_pe['yield(comp_analysis_ev)'] = (means['EV/EBIT']-db_pe['EV/EBIT'])/means['EV/EBIT']*100
        db_pe= db_pe[(db_pe['P/E'] > 0) & 
                (db_pe['P/E'] < means['P/E']) & 
                (db_pe['EV/EBIT'] > 0) &
                (db_pe['EV/EBIT'] < means['EV/EBIT']) & 
                (db_pe['EV/EBIT'] < db_pe['P/E'])] #& 
                #(db_pe['ROE'] > means['ROE'])]
        return db_pe
    def _calculate_via_comparative_p_fcf_analysis(self):
        db_p_fcf = self._db.copy(deep=True)
        db_p_fcf.drop(['P/BV', 'P/S', 'P/E', 'ROE'], inplace=True, axis=1)
        db_p_fcf = db_p_fcf[db_p_fcf['P/FCF'] > 0]
        means = db_p_fcf.mean()
        db_p_fcf['yield(comp_analysis_p_fcf)'] = (means['P/FCF']-db_p_fcf['P/FCF'])/means['P/FCF']*100
        db_p_fcf = db_p_fcf[(db_p_fcf['P/FCF'] < means['P/FCF'])]
        return db_p_fcf
    def _calculate_via_comparative_ps_analysis(self):
        db_ps = self._db.copy(deep=True)
        db_ps.drop(['P/BV', 'EV/EBIT', 'ROE'], inplace=True, axis=1)
        means = db_ps.mean()
        db_ps = db_ps[(db_ps['P/S'] < means['P/S'])]
        db_ps['yield(comp_analysis_p_s)'] = (means['P/S']-db_ps['P/S'])/means['P/S']*100
        return db_ps
    def _calculate_via_net_assets(self):
        db_bv = self._db.copy(deep=True)
        db_bv.drop(['P/E', 'EV/EBIT', 'ROE', 'P/S'], inplace=True, axis=1)
        means = db_bv.mean()
        db_bv = db_bv[(db_bv['P/BV'] < self.p_bv)]
        p_bv_data = [self.p_bv]*len(db_bv)
        p_bv_column = pd.Series(data=p_bv_data,index=db_bv.index)
        db_bv['yield(net_assets_classic)'] = (p_bv_column-db_bv['P/BV'])/p_bv_column*100
        return db_bv
    def process(self):
        self._preprocess()
        db_pe = self._calculate_via_comparative_pe_analysis()
        db_ps = self._calculate_via_comparative_ps_analysis()
        db_p_fcf = self._calculate_via_comparative_p_fcf_analysis()
        db_bv = self._calculate_via_net_assets()
        db_aggr_data = list(map(lambda i: i, 
                                filter(lambda u: u in list(db_pe['Название'].values) and 
                                       u in list(db_p_fcf['Название'].values) and 
                                       u in list(db_ps['Название'].values) and 
                                       u in list(db_bv['Название'].values), list(self._db['Название'].values)))) 
        db_aggr_data = '\n'.join(db_aggr_data)
        self._out.write(f'Results:\nComparative analysis via P/E(EV/EBIT)\n{db_pe}\n\n')
        self._out.write(f'Results:\nComparative analysis via P/FCF\n{db_p_fcf}\n\n')
        self._out.write(f'Results:\nComparative analysis via P/S\n{db_ps}\n\n')
        self._out.write(f'Results:\nComparative analysis via net assets\n{db_bv}\n\n')
        self._out.write(f'Final results:\n{db_aggr_data}\n\n')
        return (db_pe, db_p_fcf, db_ps, db_bv, db_aggr_data)
    
if __name__=="__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-csv_db", dest="csv_db", type=str)
    arg_parser.add_argument("-out_file", dest="out_file", type=str)
    args = arg_parser.parse_args()
    gen_analysis = GeneralFundamentalAnalysis(args.csv_db, args.out_file)
    miltu_av_dict = gen_analysis.process()
    print(miltu_av_dict)