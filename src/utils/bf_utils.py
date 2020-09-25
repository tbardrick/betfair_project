# import packages
import json
from pathlib import Path, PurePath 
from betfairlightweight import APIClient

# setting paths
project_dir = Path.cwd().parents[2]
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