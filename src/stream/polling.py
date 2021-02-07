# import packages
from utils import bf_utils
from betfairlightweight import filters
import pandas as pd
import time

# logging in
trading = bf_utils.api_login()

# grab a horse race - soonest chosen?
market_catalogues = trading.betting.list_market_catalogue(
    filter=filters.market_filter(
        event_type_ids=[7],  # filter on just horse racing # assumes horse racing is event_type = 7
        market_countries=["GB"],  # filter on just GB countries
        market_type_codes=["WIN"],  # filter on just WIN market types
    ),
    market_projection=[
        "MARKET_START_TIME",
        "RUNNER_DESCRIPTION",
    ],  # runner description required
    max_results=1,
)

# race/market info
race_info = {}
for m in market_catalogues:
    race_info['id'] = m.market_id
    # race_info['start'] = m.market_start_time
    # race_info['runners'] = [(r.selection_id, r.runner_name) for r in m.runners]


t_end = time.time() + 60 * 10 # 10 mins

# if start time is now then run for 10 mins... 
while time.time() < t_end: 
    # race/market price info
    market_books = trading.betting.list_market_book(
        market_ids=[race_info['id']],
        price_projection=filters.price_projection(
            price_data=filters.price_data(ex_all_offers=True) # what other options?
        ),
    )

    market_info = {}
    for mb in market_books:
        market_info['id'] = mb.market_id
        market_info['inplay'] = mb.inplay
        market_info['status'] = mb.status
        # market_info['matched'] = mb.total_matched

        market_info['a2b_prices'] = [r.ex.available_to_back[0].price if r.ex.available_to_back else 1.01 for r in mb.runners]
        # market_info['a2b_sizes'] = [r.ex.available_to_back[0].size if r.ex.available_to_back else 0 for r in mb.runners]
        # market_info['a2l_prices'] = [r.ex.available_to_back[0].price if r.ex.available_to_back else 1.01 for r in mb.runners]
        # market_info['a2l_sizes'] = [r.ex.available_to_back[0].size if r.ex.available_to_back else 0 for r in mb.runners]


    print(race_info['id'], market_info['id'], market_info['inplay'], market_info['status'])
    print(market_info['a2b_prices'])

    book = round(sum([round(1/o, 5) for o in market_info['a2b_prices']]), 3)

    print(book)


# add in NR catch by len of runners in m, different to length of runner in mb_info
# way of determining stream input per second