import SimpleHTTPServer
import SocketServer
import sys

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        splited_requestline = self.requestline.split()
        print splited_requestline
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            port = 80
    else:
        port = 80
    Handler = ServerHandler
    SocketServer.TCPServer(("", port), Handler).serve_forever()