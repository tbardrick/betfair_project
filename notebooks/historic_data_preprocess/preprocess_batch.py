
# importing packages
import json
from pathlib import Path, PurePath 
import glob

import betfairlightweight
from betfairlightweight import filters

import datetime
import re

import pandas as pd
import numpy as np

from bz2 import BZ2File 

#### logging in
project_dir = Path.cwd().parents[1]
logins_dir = project_dir / 'api_logins.json'

with open(logins_dir) as f:
    login_dict =  json.load(f)
    
trading = betfairlightweight.APIClient(username=login_dict['my_username'],
                                       password=login_dict['my_password'],
                                       app_key=login_dict['my_app_key'],
                                       certs=login_dict['certs_path'])

trading.login()

### retreive api list
data_dicts = trading.historic.get_my_data()

adv_range = [d['forDate'] for d in data_dicts if d['plan'] == 'Advanced Plan']
adv_min_date = datetime.datetime.strptime(min(adv_range), '%Y-%m-%dT%H:%M:%S')

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  
    return next_month - datetime.timedelta(days=next_month.day)

adv_max_temp = datetime.datetime.strptime(max(adv_range), '%Y-%m-%dT%H:%M:%S')
adv_max_date = last_day_of_month(adv_max_temp) 

adv_file_list = trading.historic.get_file_list(
    "Horse Racing",
    "Advanced Plan",
    from_day=adv_min_date.day,
    from_month=adv_min_date.day,
    from_year=adv_min_date.year,
    to_day=adv_max_date.day,
    to_month=adv_max_date.month,
    to_year=adv_max_date.year,
    market_types_collection=["WIN"],
    countries_collection=["GB"],
    file_type_collection=["M"],
)
print("No. markets to collect :", len(adv_file_list))


### downloading data
adv_dir = project_dir / 'data' / 'raw' / 'api' / 'advanced'
adv_downloaded_files = [Path(f).name for f in adv_dir.glob("*.bz2")] # all files downloaded

for file in adv_file_list: 
    if Path(file).name not in adv_downloaded_files: 
        print(file)
        download = trading.historic.download_file(file_path = file, store_directory = adv_dir)
        print(download)

print('All files downloaded!')

### decompressing data
adv_extfile_dirs = []

for file in glob.glob(str(adv_dir) + '/*.bz2'): # change this? dont if already processed?
    try:
        zipfile = BZ2File(file) # open the file
        data = zipfile.read() # get the decompressed data
        newfilepath = file.split('.bz2')[0] # removing the extension and saving without a filetype
        open(newfilepath, 'wb').write(data) # write an uncompressed file
        adv_extfile_dirs.append(newfilepath)
        zipfile.close()
    except OSError:
        print("File not processed : ", file)
        pass

### creating datframe (via batch)
processed_files = glob.glob(str(adv_dir) + '/*[!.bz2]')
print(len(processed_files))





























