
def application(env, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ["It's worked.\n"]

if __name__ == "__main__":
    http = WSGIServer()
    http.bind(("localhost", 9001))
    http.serv(application)
    http.start()