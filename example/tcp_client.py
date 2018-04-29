from ion import TCPClient
import ion

class MyHandler(StreamHandler):
    def setup(self):
        pass

    def handle(self, stream):
        pass

    def finish(self):
        pass

if __name__ == "__main__":
    client = TCPClient()
    client.connect("python.org", 80)
    client.handle(MyHandler)
    ion.run()