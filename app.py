from flask import Flask, Response, request
from pydantic import BaseModel, Field
from nsepython import *
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title="NSE API", version="1.0.0")
app = OpenAPI(__name__, info=info)

baseUrl = "https://www.nseindia.com/api"
app.logger.setLevel(logging.DEBUG)


@app.get('/getStockIndicesList', summary="Get stock Indices")
def getStockIndicesList():
    request_url = baseUrl + '/equity-master'
    try:
        response = nsefetch(request_url)
    except requests.exceptions.JSONDecodeError:
        logging.error("EXCEPTION : URL : " + request_url)
        return Response(status=404)
    if len(response) == 0:
        logging.error("No data found : URL : " + request_url)
        return Response(status=404)
    else:
        return response


class OnlyIndexParam(BaseModel):
    index: str = Field(None, description='Stock Index')


@app.get('/getEquityBasedOnIndex', summary="Get Stocks based on Index")
def getEquityBasedOnIndex(query: OnlyIndexParam):
    if query.index is None:
        return Response(response="index is mandatory parameter", status=400)

    request_url = baseUrl + '/equity-stockIndices?index=' + requests.utils.quote(query.index)
    response = nsefetch(request_url)
    if len(response) == 0:
        logging.error("No data found : URL : " + request_url)
        return Response(status=404)
    else:
        return response['data']


class StockHistoryParams(BaseModel):
    symbolName: str = Field(None, description='Stock Symbol Name')
    fromDate: str = Field(None, description='From Date')
    toDate: str = Field(None, description='To Date')


@app.get('/getStockHistory', summary="Get a stock's history, up to a year")
def getStockHistory(query: StockHistoryParams):
    symbol = query.symbolName
    fromDate = query.fromDate
    toDate = query.toDate
    if (symbol is None) or (fromDate is None) or (toDate is None):
        return Response(response="index, fromDate and toDate [DD-MM-YYYY] are mandatory parameters", status=400)
    request_url = (baseUrl + "/historical/cm/equity?symbol=" + requests.utils.quote(symbol) +
                   '&series=[%22EQ%22]&from=' + fromDate + '&to=' + toDate)
    response = nsefetch(request_url)
    print(response)
    if len(response) == 0:
        logging.error("No data found : URL : " + request_url)
        return Response(status=404)
    else:
        if 'error' in response.keys():
            logging.error(response['showMessage'])
            return Response(status=400, response=response['showMessage'])
        else:
            return response['data']


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
