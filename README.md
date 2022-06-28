# API Assets

Api colaborativa sobre activos financieros listados en Yahoo Finance. 
Base de datos localizada en Alphacast.

## Descripción
Se trata de una API colaborativa sobre distintos tipos de activos, los cuales tienen como año base el 2014.
La base de datos se encuentra alojada en Alphacast: https://www.alphacast.io/datasets/29828.
La API se encuentra montada en el servidor Heroku.

Originalmete no cuenta con ningún activo cargado. A medida que los usuarios la van utilizando pueden cargar Activos, así como actualizar la fecha de los que se encuentran cargados y también eliminarlos de la base, mediante los diferentes endpoints de la APP.

Los inputs de la API son los tickers que se encuentran listados en YAHOO FINANCE. Debe tomarse la estructura de los mismos para los diferentes endpoints de la aplicación.

## Endpoints
- HOME: (https://fastapi-activos.herokuapp.com/) --> WELCOME
- GET: /assets --> Listado de activos que se encuentran actualmente  en la base de datos
- GET: /assets/{asset}/{year} -->Obtencion de los datos financieros por activo y año seleccionado
- GET: /date/asset/ --> Obtención de la ultima fecha que se encuentra cargada en la base de datos para el activo seleccionado
- PUT: /asset --> Actualizar la data para un activo seleccionado que ya se encuentra en la base de datos
- POST: /asset --> Incorporar a la base de datos un activo seleccionado por el usuario de la API
- DELETE: /asset --> Eliminar de la base de datos la información para el activo seleccionado por el usuario de la API

Para mayor detalle, acceder al la documentación de la API: https://fastapi-activos.herokuapp.com/docs

![image](https://user-images.githubusercontent.com/69882938/176073259-e8ad9f75-104f-4d34-b185-d488f4cce962.png)


