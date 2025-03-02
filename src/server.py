from lib.microWebSrv import MicroWebSrv


@MicroWebSrv.route("/time")
def route_time(httpClient, httpResponse):
    import utime

    httpResponse.WriteResponseJSONOk(
        {
            "time": utime.localtime(),
        }
    )
