# import packages
import json
from pathlib import Path, PurePath 
from betfairlightweight import APIClient
from betfairlightweight import filters

# setting paths
project_dir = Path.cwd().parents[0]
logins_dir = project_dir / 'api_logins.json'

# defining functions
def api_login(login_path = logins_dir):

    with open(logins_dir) as f:
        login_dict =  json.load(f)

    trading = APIClient(username=login_dict['my_username'],
                                           password=login_dict['my_password'],
                                           app_key=login_dict['my_app_key'],
                                           certs=login_dict['certs_path'])

    trading.login()
    print('Login Succesful.')

    return(trading)

trading = api_login()

def grab_market_id():
    # - soonest chosen?
    mb = trading.betting.list_market_catalogue(
        filter=filters.market_filter(
            event_type_ids=[7],  # filter on just horse racing # assumes horse racing is event_type = 7
            # market_countries=["GB"],  # filter on just GB countries
            market_type_codes=["WIN"],  # filter on just WIN market types
        ),
        market_projection=[
            "MARKET_START_TIME",
            "RUNNER_DESCRIPTION",
        ],  # runner description required
        max_results=1,
    )[0]

    print(f"Market ID : {mb.market_id}")
    print("Race info :", mb.market_name, mb.market_start_time)
    return mb.market_id