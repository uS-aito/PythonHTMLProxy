#coding: utf-8
import SimpleHTTPServer
import SocketServer
import sys
import urllib2
import re

class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        # スタブ用返信を送信
        # self.send_response(200)
        # self.end_headers()
        # self.wfile.write("It Works!\r\n")

        # リクエスト取得
        splited_requestline = self.requestline.split()
        print "<< HTTP Request >>"
        print splited_requestline
        print ""

        # ヘッダ取得
        splited_request_headers = str(self.headers).split("\r\n")
        print "<< HTTP Request Header >>"
        print splited_request_headers
        print ""

        # ヘッダ整形
        dict_header = {}
        for header in splited_request_headers[:-1]:     # ヘッダ末尾の空行まで含むため
            splited_request_header = header.split(": ")
            dict_header.update({splited_request_header[0]:splited_request_header[1]})
        print "<< HTTP Header in Dictionary >>"
        print dict_header
        print ""
    
        # リクエストurlを取得
        url_pattern = r"https*://.*[:[0-9]*]?/"
        re_match_result = re.match(url_pattern,splited_requestline[1])
        if re_match_result:
            url = re_match_result.group()
        else:
            print "Any url does not exist in request line."
            exit(-1)

        # ヘッダくっつけて投げる
        req = urllib2.Request(url=url,headers=dict_header)
        response = urllib2.urlopen(req)

        # レスポンス確認
        print "<< HTTP Response >>"
        print (response.code, response.msg) # コードとメッセージ
        print ""
        response_info = response.info()     # レスポンスヘッダ
        print "<< HTTP Response Header >>"
        print response_info
        print ""
        response_data = response.read()     # レスポンスボディ
        print "<< HTTP Response Body >>"
        print response_data

        # レスポンスをクライアントに返す
        # httpバージョンとコード、メッセージを返す
        self.send_response(code=response.code, message=response.msg)
        # ヘッダを返す
        splited_response_headers = str(response_info).split("\r\n")
        for response_header in splited_response_headers[:-1]:
            splited_response_header = response_header.split(": ")
            self.send_header(splited_response_header[0],
                splited_response_header[1])
        # ヘッダをクローズする
        self.end_headers()
        # レスポンスを返す
        self.wfile.write(response_data)
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
