import betfairlightweight
import os
from betfairlightweight import filters
import pandas as pd
from bf_processing import process_runner_books


script_path = os.path.abspath(__file__) # i.e. /path/to/dir/foobar.py
script_dir = os.path.split(script_path)[0] #i.e. /path/to/dir/
certs_path = os.path.join(script_dir, "certs")

#create trading instance
trading = betfairlightweight.APIClient(username = "TBARDRICK",
                                       password = "Royalm22",
                                       app_key = "fsGzlDIhdkoSjbZR",
                                       certs = certs_path)

#
trading.login()

# 
horse_racing_event_type_id = trading.betting.list_event_types(
    filter=filters.market_filter(
        text_query='Horse Racing'
    )
)
#
for event_type in horse_racing_event_type_id:
    print(event_type.event_type.id, event_type.event_type.name, event_type.market_count) # prints id, name and market count
    horse_racing_id = event_type.event_type.id

    # list all horse racing market catalogues
    market_catalogues = trading.betting.list_market_catalogue(
        filter=filters.market_filter(
            event_type_ids=[horse_racing_id],  # filter on just horse racing
#             market_countries=['GB'],  # filter on just GB countries
            market_type_codes=['WIN'],  # filter on just WIN market types
        ),
        
        market_projection=['MARKET_START_TIME', 'RUNNER_DESCRIPTION'],  # runner description required
        max_results=100
    )

    print('%s market catalogues returned' % len(market_catalogues))

#
market_IDs = []
market_start_times = []
market_names = []
runner_dict = {}

for market_catalogue in market_catalogues:
    market_IDs = market_IDs + [market_catalogue.market_id]
    market_names = market_names + [market_catalogue.market_name]
    market_start_times.append(market_catalogue.market_start_time)
    
    for runner in market_catalogue.runners:
        runner_dict[runner.selection_id] = runner.runner_name
    
all_runners_df = pd.DataFrame()  # create an empty dataframe to append other dfs to

# market book request
for market,time, name in zip(market_IDs, market_start_times, market_names):
    
    # Create a price filter. Get all traded and offer data
    price_filter = filters.price_projection(
        price_data=['EX_BEST_OFFERS']
    )
    
    market_books = trading.betting.list_market_book(
        market_ids=[market],
        price_projection=price_filter
    )
    
    # append the new market book runners to the final dataframe
    market_book = market_books[0]
    runners_df = process_runner_books(market_book.runners)
    runners_df['Event_ID'] = market
    runners_df['Event Time'] = time
    runners_df['Event Name'] = name
    all_runners_df = all_runners_df.append(runners_df, ignore_index=True)

all_runners_df['Selection Name'] = all_runners_df['Selection ID'].map(runner_dict)

print(all_runners_df.columns)




