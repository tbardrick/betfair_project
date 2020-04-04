# Betfair Exchange Trading Project

_This project builds a Betfair Exchange trading agent that executes market orders based on 'pre-specified' criteria derived from previous market data._

__File Structure__

The folder/file structure & naming conventions are taken from: https://drivendata.github.io/cookiecutter-data-science/.

- `data` : Stores samples of data here. Source data is to be saved locally in MySQL database.

- `notebooks` : Contains jupyter notebooks to document data analysis, general research and model testing.

- `src` : Contains scripts for the trading bot that connects, pulls data and places bets on the Betfair API.

__Login Credentials__

Credentials should be stored within `.json` files at the git root directory and follow the format below;

`sql_logins.json` :
```
{ 
"UID" : "YOUR_USERNAME",
"PWD" : "YOUR_PASSWORD",
"DB" : "YOUR_DATABASE_NAME"
}
```

`api_logins.json` :
```
{ 
"my_username" : "YOUR_BETFAIR_USERNAME", 
"my_password" : "YOUR_BETFAIR_PASSWORD", 
"my_app_key" : "YOUR_APP_KEY", 
"certs_path" : "YOUR_CERTIFICATE_PATH"
}
```

__Data__

The historical market data is taken from the Betwise Smartform Racing Database : https://www.betwise.co.uk/smartform.

The daily data is streamed using the `betfairlightweight` package : https://github.com/liampauling/betfair.


__Packages__

The necessary packages/dependencies to be installed are:
- `betfairlightweight` : Lightweight, super fast (uses c libraries) pythonic wrapper for Betfair API-NG allowing all betting operations (including market and order streaming) and account operations.
- `sqlalchemy`
- `pymysql`
- `pandas`
- `numpy`
- `scikit`

...
