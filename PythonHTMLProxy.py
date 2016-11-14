#coding: utf-8
import SimpleHTTPServer
import SocketServer
import sys

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 返信を送信
        self.send_response(200)
        self.end_headers()
        self.wfile.write("It Works!\r\n")

        # リクエスト取得
        splited_requestline = self.requestline.split()
        print splited_requestline

        # ヘッダ取得
        splited_headers = str(self.headers).split("\r\n")
        print splited_headers
        return

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            port = 80
    else:
        port = 80
    Handler = ServerHandler
    print "Starting server in " + str(port)
    SocketServer.TCPServer(("", port), Handler).serve_forever()
