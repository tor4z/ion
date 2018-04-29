
class MyHTTPHandler(HTTPHandler):
    def GET(self):
        return "It's worked."

if __name__ == "__main__":
    http = HTTPServer()
    http.bind(("localhost", 9000))
    http.serv("/", MyHTTPHandler)
    http.start()