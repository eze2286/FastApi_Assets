#Python
from numpy import test
from typing import Text
import json
import datetime
import pandas as pd
from build_dataset import list_assets, get_dataset, market_data, acciones_urls, transformacion_datos, alphacast,upload_data_alphacast
#Pydantic
from pydantic import BaseModel
from pydantic import Field
#FastAPI
from fastapi import FastAPI, HTTPException
from fastapi import Path, Query, Body

tags_metadata = [
  {
    "name": "activos financieros",
    "description": "activos endpoint",
    "externalDocs": {
            "description": "Fuente: Alphacast",
            "url": "https://www.alphacast.io/datasets/29828",
        }, 
  }
]

app = FastAPI(title="API Activos Financieros (base = 2014)",
              description= "Obtencion de métricas sobre activos financieros listados o a listar a pedido del usuario",
              version = "0.0.1",
              openapi_tags=tags_metadata)

# Base Post Model
class Post(BaseModel):
    asset_codes:str = Field(..., min_length=1, example = "TSLA")

##############WELCOME#################################################
@app.get('/',
        summary="Welcome to Financia API",
        tags=["Home"]
 )
async def welcome_api():
    """API colaborativa sobre Activos Financieros listados en Yahoo Finance. Utilizar los códigos de cada activo
    que se utilizan en su web: https://finance.yahoo.com/
    """
    return "Welcome to API from financial assets"
##############ASSET###################################################
@app.get('/assets',
summary="All Tickers",
 tags=["Tickers"]
 )
async def get_tickers():
    """
    Listado de activos que se encuentran actualmente en la base de datos
    """
    list_of_assets = list_assets()
    return list_of_assets
##############INFO BY ASSET AND YEAR##################################
@app.get(
    path='/assets/{asset}/{year}',
    summary="Info Asset by year",
    tags=["Tickers"])
async def get_asset_info_by_year(
    asset:str = Path(..., title="Activo",
                     description="Ingresar un activo cuyo ticker se encuentre en YFinance", min_length=1,
                     example="TSLA"),
    year:int = Path(..., title="Año solicitado", gt=2000, example=2022)
     ):
    """
    Obtencion de los datos financieros por activo y año seleccionado
    """
    df_alphacast = get_dataset()
    df_filter = df_alphacast[(df_alphacast["Activo"]==asset) & (df_alphacast["Fecha"]>=f"{year}-01-01")
                              & (df_alphacast["Fecha"]<=f"{year}-12-31")]
    if len(df_filter)!=0:        
        js =  json.loads(df_filter.to_json(orient = 'records'))
        return js
    raise HTTPException(status_code=404, detail="Asset or Year not found")
##############LAST DAY LOAD BY ASSET##################################
# @app.get('/date/asset/{asset}')
@app.get(
    path='/date/asset/',
    summary="Last date for ASSET",
    tags=["Tickers"]
     )
async def get_last_day_for_asset(
    asset:str = Query(..., min_length=1, title="Activo solicitado", 
                      description="Ingresar un activo cuyo ticker se encuentre en YFinance",
                      example="TSLA")
    ):
    """
    Obtención de la ultima fecha que se encuentra cargada en la base de datos para el activo seleccionado
    """
    df_alphacast = get_dataset()
    data_filter = df_alphacast[df_alphacast["Activo"]==asset]
    if len(data_filter)!=0:
        last_asset_day = data_filter["Fecha"].tolist()[-1]
        print(last_asset_day)
        return {f"The last date load for {asset} is ":f"{str(last_asset_day)}"}
    raise HTTPException(status_code=404, detail="Asset not found") 

##############LOAD ASSET##############################################
@app.post(
path='/asset',
summary="Post a ASSET",
tags=["Tickers"]
)
async def post_new_asset(
    asset_codes:Post = Body(...)
    ):
    """
    Incorporar a la base de datos un activo seleccionado por el usuario de la API
    """
    asset = asset_codes.dict()["asset_codes"]
    list_of_assets = list_assets()
    if asset not in list_of_assets:
        try:    
            df_with_new_asset = transformacion_datos(asset)        
            return {f"Asset <<{asset}>> ": "was loaded successfully"}
        except:
            raise HTTPException(status_code=404, detail="Asset not found")
    else:
        return ({f"Asset {asset} ": "is already listed in the database"})

##############UPLOAD ASSET##################################
@app.put(
    path='/asset',
    summary="Update a ASSET",
    tags=["Tickers"]
    )
async def upload_asset(
    asset_codes:Post = Body(..., title="Activo a actualizar", 
                           description="Ingresar un activo cuyo ticker se encuentre en YFinance")
    ):
    """
    Actualizar la data para un activo seleccionado que ya se encuentra en la base de datos
    """
    df_alphacast = get_dataset()
    # asset = asset_codes.dict()["asset_codes"]
    asset = asset_codes.dict()["asset_codes"]
    try:
        data_filter = df_alphacast[df_alphacast["Activo"]==asset]
        last_asset_day = data_filter["Fecha"].tolist()[-1]
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        list_of_assets = list_assets()       
        if asset in list_of_assets:
            if (last_asset_day!=today):
                transformacion_datos(asset)
                # df_upload = market_data(asset, last_asset_day, today)                
                # last_asset_day_upload = df_upload.index[-1].strftime("%Y-%m-%d")
                # if (last_asset_day_upload != last_asset_day):
                    # print(df_upload.index[-1].strftime("%Y-%m-%d"))                
                # upload_dataset = upload_data_alphacast(df_upload, False)
                # print("ESTOY ACA")

                return {f"{asset}": "was updated successfully"}
            else:
                return {f"the asset {asset}": "is updated"}
            # else:
            #     return f"{asset} the asset is updated"
        else:
            raise HTTPException(status_code=404, detail="Asset not in list, shoul be load before upload him")
    except:        
        raise HTTPException(status_code=404, detail="the asset is wrong or should be upload")

##############DELETE ASSET##################################
@app.delete(
    path='/asset/{asset_code}',
    summary="Delete a ASSET",
    tags=["Tickers"]
    )
async def delete_asset(
    asset_code:str = Path(..., title="Activo", description="Activo el cuál se busca eliminar",
                          min_length=1, example="TSLA")
    ):
    """
    Eliminar de la base de datos la información para el activo seleccionado por el usuario de la API
    """
    df_alphacast = get_dataset()
    list_of_assets = list_assets()
    if asset_code in list_of_assets: 
        data_filter = df_alphacast[df_alphacast["Activo"]!=asset_code]
        upload_data_alphacast(data_filter, True)
        return {f"{asset_code}" : "was deleted successfuly"}
    else:
        raise HTTPException(status_code=404, detail="Asset not found")

 



# prueba = list_assets
