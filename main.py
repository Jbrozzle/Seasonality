import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose, DecomposeResult
import requests
import numpy as np
import dateutil
import matplotlib.pyplot as plt

workstation = "MAC"

if workstation == "PC":
    subcomponents = r"C:\Users\joshb\Desktop\RPI Forecasting\RPI_Subcomponents.xlsx"

if workstation == "MAC":
    subcomponents = r"/Users/Josh/Desktop/RPI_Forecaster/RPI_Subcomponents.xlsx"

subcomponent_df = pd.read_excel(subcomponents)
codes = pd.read_excel(subcomponents)['Code_TS']
descriptions = pd.read_excel(subcomponents)['Description']

this_desc = 'which'

these_codes = subcomponent_df[subcomponent_df['Description'].str.contains(this_desc)]['Code_TS']

def retrieve(timeseries_id):
    api_endpoint = "https://api.ons.gov.uk/timeseries/"
    api_params = {'dataset': 'MM23',
                  'time_series': timeseries_id}
    url = (api_endpoint + '/' + api_params['time_series'] + '/dataset/' + api_params['dataset'] + '/data')

    data = requests.get(url).json()
    data = pd.DataFrame(pd.json_normalize(data['months']))
    data['value'] = data['value'].astype(float)
    data['date'] = pd.to_datetime(data['date'])

    data['log_ret'] = np.log(data.value) - np.log(data.value.shift(1))
    data['Month Index'] = pd.DatetimeIndex(data['date']).month
    data['Year Index'] = pd.DatetimeIndex(data['date']).year
    data['pct change'] = data['value'].pct_change()

    data['Easter'] = data['Year Index'].apply(dateutil.easter.easter)
    data['Easter Month'] = pd.DatetimeIndex(data['Easter']).month
    data['Easter Day'] = pd.DatetimeIndex(data['Easter']).day
    data['Easter Regressor'] = data['Easter Month'] = data.apply(
        lambda row: int(row['Month Index'] == row['Easter Month']), axis=1)

    return data

for i in range(len(these_codes)):
    this_code = these_codes.iloc[i]
    this_code_df = retrieve(this_code)
    analysis = this_code_df['value']
    analysis.index = pd.to_datetime(this_code_df['date'])

    date_from = '01/01/2018'
    analysis = analysis[date_from:]

    decompose_result_mult = seasonal_decompose(analysis, model="additive")

    # trend = decompose_result_mult.trend
    # seasonal = decompose_result_mult.seasonal
    residual = decompose_result_mult.resid

    fig = decompose_result_mult.plot()

    fig.suptitle(subcomponent_df[subcomponent_df['Description'].str.contains(this_desc)].iloc[i]['Description'])
    plt.show()