# Betfair Exchange Trading Project

_This project builds a Betfair Exchange trading agent that executes market orders based on 'pre-specified' criteria derived from previous market data._

__File Structure__

The folder/file structure & naming conventions are taken from 'Cookiecutter Data Science' : https://drivendata.github.io/cookiecutter-data-science/ 

__Data__

The historical market data is taken from the Betwise Smartform Racing Database : https://www.betwise.co.uk/smartform.

The daily data is streamed using the ```betfairlightweight``` package : https://github.com/liampauling/betfair.


__Packages__

The necessary packages/dependencies to be installed are:
- ```betfairlightweight``` : Lightweight, super fast (uses c libraries) pythonic wrapper for Betfair API-NG allowing all betting operations (including market and order streaming) and account operations.
- ```sqlalchemy```
- ```pymysql```
- ```pandas```
- ```numpy```
- ```scikit```

...
