### Retreving downloadable historic data from Betfair

# importing packages
import sys
from pathlib import Path
import betfairlightweight
import datetime
from bz2 import BZ2File 

# add utils modules to import paths
project_dir = Path.cwd().parents[2]
sys.path.append(str(project_dir / 'src'/ 'utils'))
from bf_utils import api_login

# where to store our advanced data#
raw_dir = project_dir / 'data' / 'raw' / 'api' / 'advanced'

# logging in
trading = api_login()

# returns list of 'data dictionaries'
while True:
    try:
        data_dicts = trading.historic.get_my_data()
        break
    except:
        print('HTML Error. Trying again...')

# calculate range of dates for advanced data
adv_range = [d['forDate'] for d in data_dicts if d['plan'] == 'Advanced Plan']

# find min date for adv_data
adv_min_date = datetime.datetime.strptime(min(adv_range), '%Y-%m-%dT%H:%M:%S')

# find max data for adv data
def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  
    return next_month - datetime.timedelta(days=next_month.day)

adv_max_temp = datetime.datetime.strptime(max(adv_range), '%Y-%m-%dT%H:%M:%S')
adv_max_date = last_day_of_month(adv_max_temp)

# list files within advanced data range (GB Data)
while True:
    try:
        adv_file_list = trading.historic.get_file_list(
            'Horse Racing',
            'Advanced Plan',
            from_day=adv_min_date.day,
            from_month=adv_min_date.day,
            from_year=adv_min_date.year,
            to_day=adv_max_date.day,
            to_month=adv_max_date.month,
            to_year=adv_max_date.year,
            market_types_collection=['WIN'],
            countries_collection=['GB'],
            file_type_collection=['M'],
            )
        print ('No. items :', len(adv_file_list))
        break
    except:
        print('HTTP Error. Trying again...')



# # check if files have been downloaded already
adv_all_files = [Path(f).name for f in adv_file_list] # all files to download
adv_downloaded_dirs = [Path(f) for f in raw_dir.glob("*.bz2")] # all downloaded file paths
adv_downloaded_files = [f.name for f in adv_downloaded_dirs]

# download files we dont have and writing uncompressed versions
for file in adv_file_list: 
    if Path(file).name not in adv_downloaded_files: 
        print(file)
        download = trading.historic.download_file(file_path = file, store_directory = raw_dir)
        print(download)
 
n_downloaded = len(adv_downloaded_files)
print(f'{n_downloaded} historical files downloaded.')

# decompressing files
adv_extfile_dirs = []
for file in adv_downloaded_dirs:
    # if file not in raw_dir.glob('/*[!.bz2]'):
    try:
        zipfile = BZ2File(file) # open the file
        data = zipfile.read() # get the decompressed data
        newfilepath = str(file).replace('.bz2', '') # removing the extension and saving without a filetype
        open(newfilepath, 'wb').write(data) # write an uncompressed file
        adv_extfile_dirs.append(newfilepath)
        zipfile.close()
    except OSError:
        print("File not processed : ", file)
        pass

n_decompressed = len([f for f in raw_dir.glob('*[!.bz2]')])
print(f'{n_decompressed} historical files decompressed.')

# logout
trading.logout()
print('Logout Successful.')

if __name__ == 'main':
     pass



