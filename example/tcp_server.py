from ino.tcpserver import TCPServer, StreamHandler
import ion

class MyHandler(StreamHandler):
    def setup(self):
        pass

    def handle(self, stream):
        pass

    def finish(self):
        pass

if __name__ == "__main__":
    server = TCPServer()
    server.bind(9000)
    server.set_hander(MyHandler)
    server.start()
    ion.run()
