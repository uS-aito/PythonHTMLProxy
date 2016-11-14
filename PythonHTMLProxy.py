#coding: utf-8
import SimpleHTTPServer
import SocketServer
import sys
import urllib2

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

        # ヘッダ整形
        dict_header = {}
        for header in splited_headers[:-1]:     # ヘッダ末尾の空行まで含むため
            splited_header = header.split(": ")
            if splited_header[0] == "Host":     # 一時的にHostヘッダを無効化
                pass                            # localhostへのリクエストを無理やりgoogleに投げているため
            else:
                dict_header.update({splited_header[0]:splited_header[1]})
        print dict_header

        # ヘッダくっつけて投げる
        url = "http://www.google.co.jp"
        req = urllib2.Request(url=url,headers=dict_header)
        response = urllib2.urlopen(req)
        print response.read()
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
