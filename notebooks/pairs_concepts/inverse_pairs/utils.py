# importing packages
import betfairlightweight
import json
import os


# defining certs path 
script_dir = os.path.dirname(os.path.abspath(__file__))
certs_path = os.path.join(script_dir, 'certs')


def trading_instance():
    ''' 
    Connect to the api.

    Requires 'api_logins.json' file and certs folder in current directory.
    '''
    with open('api_logins.json') as f:
        login_dict =  json.load(f)

    trading = betfairlightweight.APIClient(username=login_dict['my_username'],
                                           password=login_dict['my_password'],
                                           app_key=login_dict['my_app_key'],
                                           certs=certs_path)

    return(trading)

def getIndexes(dfObj, value):
    """ Get index positions of value in dataframe i.e. dfObj."""
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.le(value)
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((str(row), str(col)))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos
