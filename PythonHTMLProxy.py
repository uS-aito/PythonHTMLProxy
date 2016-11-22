#coding: utf-8
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import sys
import urllib2
import re
import threading

class ServerHandler(BaseHTTPRequestHandler):
    def handle_http_proxy(self,method):
        # スタブ用返信を送信
        # self.send_response(200)
        # self.end_headers()
        # self.wfile.write("It Works!\r\n")

        # リクエスト取得
        splited_requestline = self.requestline.split()
        print "<< HTTP Request >>"
        print splited_requestline, "\n"

        # ヘッダ取得
        splited_request_headers = str(self.headers).split("\r\n")
        print "<< HTTP Request Header >>"
        print splited_request_headers, "\n"

        # ヘッダ整形
        dict_request_header = {}
        for header in splited_request_headers[:-1]:     # ヘッダ末尾の空行まで含むため
            splited_request_header = header.split(": ")
            dict_request_header.update({splited_request_header[0]:splited_request_header[1]})
        print "<< HTTP Header in Dictionary >>"
        print dict_request_header, "\n"
    
        # リクエストurlを取得
        url_pattern = r"[https?://]?.*[:[0-9]*]?/?"
        re_url_match_result = re.match(url_pattern,splited_requestline[1])
        if re_url_match_result:
            url = re_url_match_result.group()
            # connectメソッドはスキームをつけてこないのでつける
            if splited_requestline[0] == "CONNECT" or splited_requestline == "connect":
                url = "https://"+url
        else:
            print "Any url does not exist in request line."
            exit(-1)

        # Content-Lengthを含むかチェック
        content_len = 0
        re_CL_patter = re.compile("Content-Length",re.IGNORECASE)  
        for key in dict_request_header.keys():
            re_CL_match_result = re_CL_patter.match(key)
            if re_CL_match_result:
                try:
                    content_len = int(dict_request_header[key])
                    http_body = self.rfile.read(content_len)
                except:
                    pass

        # プロキシを無視するよう設定
        unproxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(unproxy_handler)
        urllib2.install_opener(opener)

        # ヘッダくっつけてメソッド指定して投げる
        if(content_len):
            req = urllib2.Request(url=url,headers=dict_request_header,data=http_body)
        else:                
            req = urllib2.Request(url=url,headers=dict_request_header)
        req.get_method = lambda : splited_requestline[0]
        response = urllib2.urlopen(req)

        # レスポンス確認
        print "<< HTTP Response >>"
        print (response.code, response.msg), "\n" # コードとメッセージ
        response_info = response.info()     # レスポンスヘッダ
        print "<< HTTP Response Header >>"
        print response_info, "\n"
        response_data = response.read()     # レスポンスボディ
        print "<< HTTP Response Body >>"
        print response_data, "\n"

        # 解析用にレスポンスヘッダ整形
        dict_response_header = {}
        splited_response_headers = str(response_info).split("\r\n")
        for header in splited_response_headers[:-1]:     # ヘッダ末尾の空行まで含むため
            splited_response_header = header.split(": ")
            dict_response_header.update({splited_response_header[0]:splited_response_header[1]})
        print "<< HTTP Response Header in Dictionary >>"
        print dict_response_header, "\n"

        # ヘッダ解釈
        # Transfer-EncodingにChunkが含まれるか確認
        is_chunked = False
        re_TE_patter = re.compile("Transfer-Encoding",re.IGNORECASE)  # HTTPヘッダは大文字小文字無視するので
        re_chunked_patter = re.compile("chunked",re.IGNORECASE)       # その設定の正規表現で検索する必要
        for key in dict_response_header.keys():
            re_TE_match_result = re_TE_patter.match(key)
            if re_TE_match_result:
                re_chunked_match_result = re_chunked_patter.match(dict_response_header[key])
                if re_chunked_match_result:
                    is_chunked = True 
                    break
        print "<< HTTP Response Header Analyse Result >>"
        print "is_chunked:", is_chunked, "\n"

        # レスポンスをクライアントに返す
        # httpバージョンとコード、メッセージを返す
        self.send_response(code=response.code, message=response.msg)
        print "DEBUG: HTTP response is send"
        # ヘッダを返す
        splited_response_headers = str(response_info).split("\r\n")
        for response_header in splited_response_headers[:-1]:
            splited_response_header = response_header.split(": ")
            self.send_header(splited_response_header[0],
                splited_response_header[1])
        print "DEBUG: HTTP header is send"
        # ヘッダをクローズする
        self.end_headers()
        print "DEBUG: HTTP header is closed"
        # レスポンスを返す
        # Chunkedが指定されている場合長さを返す
        if is_chunked:
            self.wfile.write("%x\r\n" % len(response_data))
        # ボディそのものを返す
        self.wfile.write(response_data+"\r\n")
        print "DEBUG: HTTP body is send"
        # Chunkedが指定されている場合0と空行を返す
        if is_chunked:
            self.wfile.write("0\r\n\r\n")
        print "DEBUG: Class Method is returned"
        return

    # handle_http_proxyを全てのmethodに対して呼び出す
    def do_GET(self):
        self.handle_http_proxy("GET")
    
    def do_HEAD(self):
        self.handle_http_proxy("HEAD")

    def do_POST(self):
        self.handle_http_proxy("POST")

    def do_PUT(self):
        self.handle_http_proxy("PUT")

    def do_DELETE(self):
        self.handle_http_proxy("DELETE")

    def do_CONNECT(self):
        self.handle_http_proxy("CONNECT")

    def do_OPTIONS(self):
        self.handle_http_proxy("OPTIONS")

    def do_TRACE(self):
        self.handle_http_proxy("TRACE")

class ThreadedHTTPProxy(ThreadingMixIn, HTTPServer):
    """ Handle requests in a separate thread. """

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            port = 80
    else:
        port = 80
    
    Handler = ServerHandler
    server = ThreadedHTTPProxy(("",port), Handler)
    print "Starting server in " + str(port)
    server.serve_forever()