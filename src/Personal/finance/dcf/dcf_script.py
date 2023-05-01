import pandas as pd
import numpy as np
import numpy_financial as npf
import re
import argparse

#add dataframe columns header parser similar to dcf_portfolio_script.py

class DCF_calc:
    @staticmethod
    def filter_db(column):
        patterns = ['capex', 'profit', 'revenue', 'earning', 'amort', 'expense']
        for pattern in patterns:
            if re.search(pattern, column, re.IGNORECASE):
                return True

        return False
    @staticmethod
    def interpolate_last_year(asset_db, filt_asset_db):

        last_year = asset_db['year'].max()

        two_last_years_db = asset_db[(asset_db['year'] == last_year) | (asset_db['year'] == (last_year - 1))]
        two_last_years_crosstab = pd.crosstab(index=two_last_years_db['year'], columns=two_last_years_db['period'])

        periods = ['Q', '6M', '9M', 'Y']
        av_periods = [per in two_last_years_db['period'].array for per in periods]
        av_periods = dict(zip(periods,av_periods))
        aggr_periods = []

        if av_periods['9M'] and av_periods['Q'] and two_last_years_crosstab.loc[last_year, '9M'] == 1:

            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == last_year) & \
                                (two_last_years_db['period'] == '9M')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & \
                                (two_last_years_db['period'] == 'Q')].index.values.astype(int)[-1])

        elif av_periods['6M'] and two_last_years_crosstab.loc[last_year, '6M'] == 1:

            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == last_year) & (
                    two_last_years_db['period'] == '6M')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == '6M')].index.values.astype(int)[-1])

        elif av_periods['Q'] and av_periods['6M'] and two_last_years_crosstab.loc[last_year, 'Q'] == 1:

            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == last_year) & (
                    two_last_years_db['period'] == 'Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == 'Q')].index.values.astype(int)[-1])
            aggr_periods.append(two_last_years_db[(two_last_years_db['year'] == (last_year - 1)) & (
                    two_last_years_db['period'] == '6M')].index.values.astype(int)[-1])

        mod_columns = list(filter(DCF_calc.filter_db, two_last_years_db.columns))
        last_year_result = two_last_years_db.loc[aggr_periods[0], :].copy()

        for i in range(1, len(aggr_periods)):
            for column in mod_columns:
                last_year_result.loc[column] += two_last_years_db.loc[aggr_periods[i], column]

        last_year_result.loc['period'] = 'Y'
        last_year_result.loc['month'] = 12

        dict_data = dict(zip(last_year_result.index, last_year_result.values))
        last_year_result = pd.DataFrame(data=dict_data, index=[max(filt_asset_db.index) + 1])

        filt_asset_db = pd.concat([filt_asset_db, last_year_result])
        return filt_asset_db

    @staticmethod
    def calculate_stock_data(asset_db):
        last_year_result = asset_db.iloc[-1, :].copy()
        stock_data_dict = {}

        for column in last_year_result.index:
            if re.search('num[1-9].??$', column, re.IGNORECASE) or re.search('price[1-9].??_day$', column, re.IGNORECASE):
                price_id = int(re.findall('[0-9]+', column)[0])
                if price_id not in stock_data_dict:
                    stock_data_dict[price_id] = {'ev_price':0}

                if re.search('num[1-9].??$', column, re.IGNORECASE) and 'num' not in stock_data_dict[price_id]:
                    stock_data_dict[price_id]['num'] = last_year_result[column]
                if re.search('price[1-9].??_day$', column, re.IGNORECASE) and 'price' not in stock_data_dict[price_id]:
                    stock_data_dict[price_id]['cur_price'] = last_year_result[column]

        min_price_id = min(stock_data_dict.keys())
        for price_id in stock_data_dict.keys():
            stock_data_dict[price_id]['stock_ratio'] = stock_data_dict[price_id]['cur_price']/stock_data_dict[min_price_id]['cur_price']

        return stock_data_dict


    def __init__(self, csv_file, betta, rf, rm, country_risk, invst_hrznt, type):

        self.betta = betta
        self.rf = rf
        self.rm = rm
        self.country_risk = country_risk
        self.invst_hrznt = invst_hrznt

        asset_db = pd.read_csv(csv_file)
        asset_db = asset_db[asset_db['type'] == type]
        filt_asset_db = asset_db[asset_db['period']=='Y']
        
        last_year = asset_db['year'].max()
        filt_last_year = filt_asset_db['year'].max()
        if last_year != filt_last_year:
            asset_db = DCF_calc.interpolate_last_year(asset_db, filt_asset_db)
        else:
            asset_db = filt_asset_db
        self.asset_db = asset_db
        self.stock_data_dict = DCF_calc.calculate_stock_data(self.asset_db)

    def calculate_wacc(self, last_year_result):

        # Calculate capital weights
        we = last_year_result['equity'] / (last_year_result['equity'] + last_year_result['total_debt'])
        wd = last_year_result['total_debt'] / (last_year_result['equity'] + last_year_result['total_debt'])
        # print(f'we1: {we}\nwd1: {wd}\n')

        #Calculate capital costs
        #CAPM
        ke = self.rf + self.betta * (self.rm - self.rf) + self.country_risk
        if last_year_result['total_debt'] > 0:
            kd = last_year_result['interest_expense'] / last_year_result['total_debt'] * 100
        else:
            kd = 0
        tax = (last_year_result['earnings_wo_tax'] - last_year_result['earnings']) / last_year_result['earnings_wo_tax']

        #WACC
        wacc = (ke * we * (1 - tax) + kd * wd) / 100

        return wacc

    @staticmethod
    def calculate_ev_dcf(asset_db, ev, wacc, invst_hrznt):
        # FCF database creation
        fcf_indexes = ['earnings', 'depr_depl_amort', 'capex', 'ebitda', 'nwc', 'delta_nwc', 'fcf']
        fcf_columns = list(asset_db['year'].apply(str).values)
        for year in range(int(asset_db['year'].max()) + 1, int(invst_hrznt) + 1):
            fcf_columns.append(str(year))
        fcf_df = pd.DataFrame(data=np.zeros((len(fcf_indexes), len(fcf_columns))), index=fcf_indexes,
                              columns=fcf_columns)

        # FCF database initialization
        init_min_max_year = [str(asset_db['year'].min()), str(asset_db['year'].max())]
        for i in fcf_indexes:
            # print(f'asset_db[i]:\n{asset_db[i]}')
            if i in ['earnings', 'depr_depl_amort', 'capex']:
                fcf_df.loc[i, init_min_max_year[0]:init_min_max_year[1]] = np.array(asset_db[i].values)
            elif i == 'ebitda':
                fcf_df.loc[i, init_min_max_year[0]:init_min_max_year[1]] = np.array(
                    asset_db['earnings_wo_tax'] + (asset_db['interest_expense'] - asset_db['interest_income']) +
                    asset_db['depr_depl_amort'])
            elif i == 'nwc':
                nwc_series = asset_db['current_assets'] - asset_db['current_liabilities']
                fcf_df.loc[i, init_min_max_year[0]:init_min_max_year[1]] = np.array(nwc_series.values)
            elif i == 'delta_nwc':
                for j in range(int(init_min_max_year[0]) + 1, int(init_min_max_year[1]) + 1):
                    fcf_df.loc[i, str(j)] = fcf_df.loc['nwc', str(j)] - fcf_df.loc['nwc', str(j - 1)]
            elif i == 'fcf':
                fcf_df.loc[i, :] = fcf_df.loc['earnings', :] + fcf_df.loc['depr_depl_amort', :] - fcf_df.loc['capex',:] - fcf_df.loc['delta_nwc', :]

        #Extrapolation coefficients calculation
        extrp_compnts = ['earnings', 'depr_depl_amort', 'capex', 'ebitda', 'nwc']
        extrp_coef = pd.Series(data=np.zeros(len(extrp_compnts)), index=extrp_compnts)
        for i in extrp_compnts:
            for j in range(int(init_min_max_year[0]) + 1, int(init_min_max_year[1])+1):
                if fcf_df.loc[i, str(j - 1)] != 0:
                    extrp_coef[i] += (fcf_df.loc[i, str(j)] - fcf_df.loc[i, str(j - 1)]) / fcf_df.loc[i, str(j - 1)]
            extrp_coef[i] = extrp_coef[i] / (int(init_min_max_year[1]) - int(init_min_max_year[0]))

        #FCF extrapolation
        ext_period = [str(int(init_min_max_year[1]) + 1), str(int(invst_hrznt))]
        for i in fcf_indexes:
            if i in extrp_compnts:
                for j in range(int(ext_period[0]), int(ext_period[1]) + 1):
                    fcf_df.loc[i, str(j)] = fcf_df.loc[i, str(j - 1)] * (1 + extrp_coef[i])
            elif i == 'delta_nwc':
                for j in range(int(ext_period[0]), int(ext_period[1]) + 1):
                    fcf_df.loc[i, str(j)] = fcf_df.loc['nwc', str(j)] - fcf_df.loc['nwc', str(j - 1)]
            elif i == 'fcf':
                fcf_df.loc[i, ext_period[0]:ext_period[1]] = fcf_df.loc['earnings',ext_period[0]:ext_period[1]] + fcf_df.loc['depr_depl_amort',ext_period[0]:ext_period[1]] - \
                                                             fcf_df.loc['capex',ext_period[0]:ext_period[1]] - fcf_df.loc['delta_nwc',ext_period[0]:ext_period[1]]

        npv = npf.npv(wacc, fcf_df.loc['fcf', ext_period[0]:ext_period[1]].values)
        ev_ebitda_multi = ev / fcf_df.loc['ebitda', init_min_max_year[1]]
        delta_invest_horizont = int(invst_hrznt) - int(init_min_max_year[1])
        tv = ev_ebitda_multi * fcf_df.loc['ebitda', ext_period[1]] / (1 + wacc) ** delta_invest_horizont
        ev_dcf = npv + tv

        return ev_dcf

    def calculate_fair_share_price(self):

       #Calculate capitalization
        last_year_result = self.asset_db.iloc[-1, :].copy()
        last_year_result['capital'] = 0
        for price_id in self.stock_data_dict.keys():
            last_year_result['capital'] += self.stock_data_dict[price_id]['cur_price']*self.stock_data_dict[price_id]['num']

       #Calculate evaluation price
        self.ev = last_year_result['capital'] + last_year_result['total_debt'] - last_year_result['cash_and_equiv']
        negative_ev = 0
        if self.ev < 0:
            self.ev += last_year_result['cash_and_equiv']
            negative_ev = 1

       # Calculate WACC
        self.wacc = self.calculate_wacc(last_year_result)

        # Net present DCF evaluation price
        self.dcf_ev = DCF_calc.calculate_ev_dcf(self.asset_db, self.ev, self.wacc, self.invst_hrznt)
        self.dcf_cap = self.dcf_ev - last_year_result['total_debt'] + last_year_result['cash_and_equiv']
        if negative_ev:
            self.dcf_cap -= last_year_result['cash_and_equiv']
        result_stock_data = dict()

        #print('Num  Current price   Evaluated price Margin,%')
        priv_num = 0
        for price_id in self.stock_data_dict.keys():
            priv_num += self.stock_data_dict[price_id]['stock_ratio']*self.stock_data_dict[price_id]['num']
        base_stock_price = self.dcf_cap/priv_num

        for price_id in self.stock_data_dict.keys():
            cur_stock_dict = {}
            cur_stock_dict['cur_price'] = self.stock_data_dict[price_id]['cur_price']
            cur_stock_dict['ev_price'] = self.stock_data_dict[price_id]['stock_ratio']*base_stock_price
            if cur_stock_dict['cur_price'] > 0:
                cur_stock_dict['margin'] = (cur_stock_dict['ev_price'] - cur_stock_dict['cur_price'])/cur_stock_dict['cur_price']*100
            else:
                cur_stock_dict['margin'] = 0
            result_stock_data[price_id] = cur_stock_dict

        self.result_stock_data = result_stock_data

        return result_stock_data



if __name__=='__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-csv_file', dest='csv_file', type=str)
    arg_parser.add_argument('-betta', dest='betta', type=float)
    arg_parser.add_argument('-rf', dest='rf', type=float)
    arg_parser.add_argument('-rm', dest='rm', type=float)
    arg_parser.add_argument('-hrznt', dest='hrznt', type=int)
    arg_parser.add_argument('-crp', dest='crp', type=float)

    args = arg_parser.parse_args()
    print(args)
    dcf_clc = DCF_calc(csv_file=args.csv_file, betta = args.betta, rf = args.rf, rm = args.rm, country_risk = args.crp, invst_hrznt=args.hrznt)
    result_stock_price = dcf_clc.calculate_fair_share_price()

    print('Num  Current price   Evaluated price Margin,%')
    for stock_id in result_stock_price.keys():
        cur_stock_data = result_stock_price[stock_id]
        print(f'{stock_id}:  {cur_stock_data["cur_price"]} {cur_stock_data["ev_price"]} {cur_stock_data["margin"]}')