### Script to process historic data

# importing packages
import sys
from pathlib import Path

# add utils modules to import paths
project_dir = Path.cwd().parents[2]
sys.path.append(str(project_dir / 'src'/ 'utils'))
from process_utils import *
from bf_utils import api_login

# where our historic raw data is stored
raw_dir = project_dir / 'data' / 'raw' / 'api' / 'advanced'
decompressed_files = raw_dir.glob('*[!.bz2]')

test_file = list(decompressed_files)[0]
print(test_file)

# login (to create 'trading' instance)
trading = api_login()


d = datadict
T_PRE = 60
T_POST = 15

listener = HistoricalListener(max_latency=None)

stream = trading.streaming.create_historical_stream(file_path=str(test_file), listener=listener)
stream.start() 
stream.stop()

print("Stream of " + test_file.name + ' completed.')

# create df
df = dict_to_df(datadict)
df = pre_filter_races(df)
df = extract_race_info(df)
df = create_timedif(df)
df = filter_timedif(df)
df = create_time_bins(df, T_PRE, T_POST)
df = runner_groupby(df, T_PRE, T_POST)

print(df)




# logout
trading.logout()
print('Logout Successful.')


if __name__ == 'main':
    pass