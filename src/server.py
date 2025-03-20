from lib.microWebSrv import MicroWebSrv
from measurements import Timestamp


@MicroWebSrv.route("/time")
def route_time(httpClient, httpResponse):
    import utime

    httpResponse.WriteResponseJSONOk(
        {
            "time": utime.localtime(),
        }
    )


@MicroWebSrv.route("/data")
def route_data(httpClient, httpResponse):
    import db

    queryParams = httpClient.GetRequestQueryParams()

    _from = None
    _to = None

    if "from" in queryParams:
        _from = Timestamp.from_str(queryParams["from"])

    if "to" in queryParams:
        _to = Timestamp.from_str(queryParams["to"])

    _db = db.DB("/sd/data.csv")
    data = _db.read(_from=_from, _to=_to)
    print(data)

    httpResponse.WriteResponseOk(contentType="text/csv", content=data)
