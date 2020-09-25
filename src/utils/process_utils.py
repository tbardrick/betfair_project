import pandas as pd
import numpy as np
import re

from betfairlightweight import StreamListener
from betfairlightweight.streaming.stream import MarketStream

# stream objects

datadict = {'Time': [],
       'MarketId' : [],
       'Status' : [],
       'Inplay' : [], 
       'SelectionId' : [],
       'LastPriceTraded' : [],
       'TotalMatched' : [],
       'BSP' : [],
       'AdjFactor' :  [],
       'RunnerStatus' : [],
       'MktTotalMatched' : [],
       'RaceInfo' : [],
       'Venue' : [],
       'BackSize': [],
       'BackPrice': [],
       'LayPrice' : [],
       'LaySize' : []
}


class HistoricalStream(MarketStream):
    # create custom listener and stream

    def _init_(self, listener):
        super(HistoricalStream, self)._init_(listener)

    def on_process(self, market_books):
        for market_book in market_books:
            for runner in market_book.runners:

                datadict['Time'].append(market_book.publish_time)
                datadict['MarketId'].append(float(market_book.market_id))
                datadict['Status'].append(market_book.status)
                datadict['Inplay'].append(market_book.inplay)
                datadict['SelectionId'].append(runner.selection_id)
                datadict['LastPriceTraded'].append(runner.last_price_traded)
                datadict['TotalMatched'].append(runner.total_matched)
                datadict['BSP'].append(runner.sp.actual_sp)
                datadict['AdjFactor'].append(runner.adjustment_factor)
                datadict['RunnerStatus'].append(runner.status)
                datadict['MktTotalMatched'].append(market_book.total_matched)
                datadict['RaceInfo'].append(market_book.market_definition.name)
                datadict['Venue'].append(market_book.market_definition.venue)
                
                atb_size = [x.size for x in runner.ex.available_to_back]
                datadict['BackSize'].append(atb_size)
                atb_price = [x.price for x in runner.ex.available_to_back]
                datadict['BackPrice'].append(atb_price)   
                atl_price = [x.price for x in runner.ex.available_to_lay]
                datadict['LayPrice'].append(atl_price)
                atl_size = [x.size for x in runner.ex.available_to_lay]
                datadict['LaySize'].append(atl_size)

class HistoricalListener(StreamListener):
    def _add_stream(self, unique_id, stream_type):
        if stream_type == "marketSubscription":
            return HistoricalStream(self)

# dataframe transformations
def dict_to_df(datadict):
    
    df = pd.DataFrame(datadict)
    
    df.sort_values(by = 'Time')
    
    df['MarketId'] = df['MarketId'].astype(str)
    df['SelectionId'] = df['SelectionId'].astype(str)
    
    df['LayPrice'] = df['LayPrice'].apply(lambda x: x[0] if x else np.nan)
    df['LaySize'] = df['LaySize'].apply(lambda x: x[0] if x else np.nan)
    df['BackPrice'] = df['BackPrice'].apply(lambda x: x[0] if x else np.nan)
    df['BackSize'] = df['BackSize'].apply(lambda x: x[0] if x else np.nan)
    
    return df


def pre_filter_races(df):
    'use it to reduce size of df (removing unnecessary) before applying transformation - speed up'
    
    # keeping only OPEN & ACTIVE markets
    df = df.loc[(df['Status'] == 'OPEN') & (df['RunnerStatus'] == 'ACTIVE')] 

    # removing prices with size < 10
    df = df.loc[(df['BackSize'] > 5) | (df['LaySize'] > 5)] 
    return df

def extract_furlongs(market_name):
    '''
    Assuming distance is always stated 1st within 'MarketName', with space followed after.
    Distance given in format of furlongs, miles or both.
    8 furlongs in a mile.
    '''
    
    distance = market_name.split(' ')[0]
    
    if 'm' in distance:
        m = distance.split('m')[0]
        distance = distance.replace(m + 'm', '')
        
        if 'f' in distance:
            f = distance.split('f')[0]
            
            return (int(m) * 8) + int(f)

        return int(m) * 8
    
    else:
        f = distance.split('f')[0]
        
        return int(f)

def extract_race_type(market_name):
    if 'Hrd' in market_name:
        return 'Hurdle'
    if 'Chs' in market_name:
        return 'Chase'
    if 'NHF' in market_name:
        return 'NHF'
    else:
        return 'Flat'

def extract_race_info(df):
    df['NoRunners'] = df.groupby('MarketId')['SelectionId'].transform('nunique')
    df['Distance'] = df['RaceInfo'].apply(lambda x: extract_furlongs(x))
    df['RaceType'] = df['RaceInfo'].apply(lambda x: extract_race_type(x))
    return df




def create_timedif(df):
    # converting to datetime
    df['Time'] = pd.to_datetime(df['Time'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

    # calculating inplay start for each race (assigning to new columns)
    df['StartTime'] = df['Time'].where(df['Inplay'] == True).groupby(df['MarketId']).transform('min')

    # calculating difference between each time point and start time
    df['TimeDif'] = (df['Time'] - df['StartTime']).astype('timedelta64[s]')

    # dropping starttime (Can be inferred by InPlay)
    df = df.drop('StartTime', 1)
    return df

def filter_timedif(df):
    # removing timpoints more than on hour before the race
    df = df.loc[df['TimeDif'] > -3600]
    
    # remove null time points
    df = df[~df['TimeDif'].isnull()]
    
    return df

def create_time_bins(df, T_pre, T_post):
    # T_pre = the number of bins to divide seconds into ~ (3600 seconds pre race)
    # T_post = the number of bins to divide seconds into ~ (60 - 580 seconds for race)

    # creating time bins pre race
    df['T_pre'] = df.where(df['Inplay'] == False).groupby('SelectionId')['TimeDif'].apply(lambda x: pd.qcut(x, T_pre, labels = [i for i in range(-T_pre, 0)])).astype(float)

    # cretaing time bins suring race
    df['T_post'] = df.where(df['Inplay'] == True).groupby('SelectionId')['TimeDif'].apply(lambda x: pd.qcut(x, T_post, labels = [i for i in range(0, T_post)])).astype(float)

    df['T'] = df['T_pre'].fillna(df['T_post']).astype(int)

    df.drop(columns = ['T_pre', 'T_post'], inplace = True)
    
    return df

def runner_groupby(df, T_pre, T_post):
    
    agg1 = {'MarketId' : 'first',
           'Venue' : 'first',
           'Distance' : 'first',
           'RaceType' : 'first',
           'BSP' : 'first',
           'NoRunners' : 'first'
            }

    df1 = df.groupby(['SelectionId']).agg(agg1).reset_index()
    df1['SelectionId'] = df1['SelectionId'].astype(str)
    
    dfs = []
    cols = ['BackSize', 'BackPrice', 'LayPrice', 'LaySize']
    cols_short = [re.sub('[^A-Z]', '', s) for s in cols]

    df2 = df.groupby(['SelectionId', 'T'])[cols].mean().reset_index()
    msk = df2.columns[~df2.columns.isin(['SelectionId','T'])]
    df2[msk] = df2[msk].apply(lambda x: round(x, 2))

    for col, col_short in zip(cols, cols_short):
        x = df2.groupby('SelectionId')[col].apply(list)
        y = pd.DataFrame(x.tolist(), index=x.index,
                     columns = [col_short +':T' + str(x) for x in range(-T_pre, 0)] + \
                               [col_short + ':T+' + str(x) for x in range(T_post)]).reset_index()
        y['SelectionId'] = y['SelectionId'].astype(str)
        dfs.append(y)

    z = pd.concat(dfs, axis =1)
    z = z.loc[:,~z.columns.duplicated()]

    final_df = df1.merge(z, on = 'SelectionId')
    
    return final_df