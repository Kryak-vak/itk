import requests

HTTP_STATUS_LINES = {
    200: "200 OK",
    201: "201 Created",
    202: "202 Accepted",
    204: "204 No Content",

    301: "301 Moved Permanently",
    302: "302 Found",
    303: "303 See Other",
    304: "304 Not Modified",
    307: "307 Temporary Redirect",
    308: "308 Permanent Redirect",

    400: "400 Bad Request",
    401: "401 Unauthorized",
    403: "403 Forbidden",
    404: "404 Not Found",
    405: "405 Method Not Allowed",
    409: "409 Conflict",
    422: "422 Unprocessable Entity",

    500: "500 Internal Server Error",
    502: "502 Bad Gateway",
    503: "503 Service Unavailable",
    504: "504 Gateway Timeout",
}


def app(environ, start_response):
    default_headers = [("Content-Type", "text/plain")]

    method = environ.get("REQUEST_METHOD")
    
    if method != "GET":
        start_response(HTTP_STATUS_LINES[405], default_headers)
        return [b"GET requests only."]
    
    path: str = environ["PATH_INFO"]
    currency: str = path.split("/")[1]
    
    if not currency:
        start_response(HTTP_STATUS_LINES[404], default_headers)
        return [b"Currency required."]

    status_code, r_text = fetch_exchange_rate(currency)
    status_line = HTTP_STATUS_LINES[status_code]

    start_response(status_line, default_headers)
    return [r_text]


def fetch_exchange_rate(currency: str) -> tuple[int, bytes]:
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    
    with requests.Session() as session:
        r = session.get(url)
    
    return r.status_code, r.content