import pandas as pd
import datetime
import numpy as np
import requests
import yfinance as yf
import time
pd.options.display.float_format = '{:.4f}'.format
pd.options.display.max_columns = 8

from alphacast import Alphacast

API_key = "ak_InwypYyuGx9GQlWNUHDf"
alphacast = Alphacast(API_key)

def get_dataset():
    df_alphacast = alphacast.datasets.dataset(29828).download_data("pandas")
    return df_alphacast

def list_assets():
    df_alphacast = alphacast.datasets.dataset(29828).download_data("pandas")
    list_assets = df_alphacast.Activo.unique().tolist()
    return list_assets

def market_data (ticker,desde,hasta):
    datos = yf.download(ticker, start=desde, end=hasta)
    return datos

ticker = "TSLA"
def acciones_urls(ticker):    
    accion = market_data(ticker,desde='2014-01-01', hasta=datetime.datetime.today().strftime("%Y-%m-%d"))
    accion = accion.reset_index()
    return(accion)

def upload_data_alphacast(df, deleteMissingFromDB=False):    
    alphacast.datasets.dataset(29828).upload_data_from_df(df.set_index(df.columns[0]), 
                 deleteMissingFromDB = deleteMissingFromDB, onConflictUpdateDB = True, uploadIndex=True)

## TRANSFORMO LOS DATAFRAMES
def transformacion_datos(ticker):
    dataframe = acciones_urls(ticker)       
    dataframe.Date = pd.to_datetime(dataframe.Date)
    dataframe = dataframe.convert_dtypes()
    dataframe.columns = ["Fecha","Apertura", "Maximo", "Minimo", "Cierre", "Cierre_Aj",
                          "Volumen"]
    dataframe = dataframe[(dataframe["Apertura"]!=0)&(dataframe["Maximo"]!=0)&(dataframe["Minimo"]!=0)&(dataframe["Cierre"]!=0)&(dataframe["Cierre_Aj"]!=0)]
      
    dataframe["SMA_20"] = dataframe["Cierre_Aj"].rolling(20).mean()            
    dataframe["Variacion"] = round(dataframe["Cierre_Aj"].pct_change()*100,2)
        
    dataframe["Volat._40"] = round(dataframe["Variacion"].rolling(40).std() * np.sqrt(250),2)
        
    dataframe["Sigma_40_m.movil_20r"] = round(dataframe["Volat._40"].rolling(20).mean(),2)
        
    dataframe["Cierre_Aj"] = dataframe["Cierre_Aj"].astype(float)
    dataframe["Rendimiento"] = ((1 + (dataframe["Cierre_Aj"].pct_change())).cumprod()-1)*100
    dataframe["Variacion"] = dataframe["Cierre_Aj"].pct_change()*100
    dataframe["Activo"] = ticker
    dataframe = dataframe.dropna(how='all')
    dataframe = dataframe.fillna(0)
    alphacast.datasets.dataset(29828).upload_data_from_df(dataframe.set_index("Fecha"), 
                 deleteMissingFromDB = False, onConflictUpdateDB = True, uploadIndex=True)
    # return dataframe     

# ACTUALIZACION DE LA DATA EN ALPHACAST
# dataframe = transformacion_datos("AAPL")
# print(dataframe)
# print(df_alphacast[(df_alphacast["Activo"]=="TSLA") & (df_alphacast["Activo"]=="TSLA")])
# print(df_alphacast[df_alphacast["Fecha"]>"2020-01-01"])

# alphacast.datasets.dataset(29828).upload_data_from_df(dataframe.set_index("Fecha"), 
#                  deleteMissingFromDB = True, onConflictUpdateDB = True, uploadIndex=True)


