#coding: utf-8
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import sys
import urllib2
import re
import threading
import socket
from contextlib import closing
import select
import urlparse

class ProxyHandler(BaseHTTPRequestHandler):

    def __init__(self,request,client_addr,server):
        # 送受信しているデータを保存する変数
        # 参照を渡したほうがスムーズなのでリストを使用
        self.recv_data = [""]
        self.send_data = [""]
        BaseHTTPRequestHandler.__init__(self,request,client_addr,server)

    # connect以外はこちら
    def handle_http_proxy(self):
        # 接続情報を保存するクラス
        self.connection_info = ConnectionInfo()
        # リクエスト取得
        splited_requestline = self.get_requestline()

        # ヘッダ取得
        splited_request_headers = self.get_header()

        # ヘッダ整形
        dict_request_header = {}
        for header in splited_request_headers[:-1]:     # ヘッダ末尾の空行まで含むため
            splited_request_header = header.split(": ")
            dict_request_header.update({splited_request_header[0]:splited_request_header[1]})
        # print "<< HTTP Header in Dictionary >>"
        # print dict_request_header, "\n"

        # ヘッダを修正
        dict_request_header["Connection"] = "Close" # TCPコネクションを継続しない
        re_PC_patter = re.compile("Proxy-Connection",re.IGNORECASE) # Proxy-Connectionヘッダを削除
        for key in dict_request_header.keys():
            re_PC_match_result = re_PC_patter.match(key)
            if re_PC_match_result:
                del dict_request_header[key]
    
        # リクエストurlを取得
        parsed_url = urlparse.urlparse(splited_requestline[1])
        if parsed_url.netloc == "":
            print "Invalid request URL"
            return
        
        # 対象サーバとTCP接続を確立
        tunnel = self.connect_tcp(parsed_url.netloc)
        if tunnel is "":
            return
        try:
            # リクエストを送信
            tunnel.send("%s %s %s\r\n" % (
                splited_requestline[0],
                urlparse.urlunparse(
                    ("","",parsed_url.path,parsed_url.params,parsed_url.query,"")),
                splited_requestline[2]
                ))
            # ヘッダを送信
            for key in dict_request_header.items():
                tunnel.send("%s: %s\r\n" % key)
            tunnel.send("\r\n")
            # パケットを中継
            self.tunnel_packet(tunnel, 300)
            
        finally:
            # リクエストを解析し格納
            self.connection_info.request = " ".join(splited_requestline)
            self.connection_info.request_header = "\r\n".join(splited_request_headers)
            self.connection_info.request_body = self.send_data[0]

            # レスポンスを解析し格納
            response_firstline_end_pos = self.recv_data[0].find("\r\n")
            response_header_end_pos = self.recv_data[0].find("\r\n\r\n")
            self.connection_info.response = \
             self.recv_data[0][:response_firstline_end_pos]
            self.connection_info.response_header = \
             self.recv_data[0][response_firstline_end_pos+1:response_header_end_pos]
            self.connection_info.response_body = \
             self.recv_data[0][response_header_end_pos+1:]

            # サーバ側・クライアント側コネクションを終了
            tunnel.close()
            self.connection.close()

        self.callback(self.connection_info)
        return

    # connectが飛んできたらこちら
    def handle_https_proxy(self):
        # リクエスト取得
        splited_requestline = self.get_requestline()

        # ヘッダ取得
        splited_request_headers = self.get_header()
    
        # 対象サーバとTCP接続を確立
        tunnel = self.connect_tcp(splited_requestline[1])
        if tunnel is "":
            return
        try:
            self.send_response(code=200, message="Connection Established")
            self.end_headers()
            self.tunnel_packet(tunnel, 300)
        finally:
            tunnel.close()
            self.connection.close()

        return
    # パケットを中継する
    def tunnel_packet(self, srv_soc, max_idle_count = 20):
        read_list = [self.connection, srv_soc]
        write_list = []
        idle_count = 0
        while True:
            idle_count += 1
            (read_list_standby, _, xlist_standby) = select.select(read_list, write_list, read_list)
            if xlist_standby:
                break
            if read_list_standby:
                for r_obj in read_list_standby:
                    if r_obj is srv_soc:
                        output_if = self.connection
                        tgt_stream = self.recv_data
                    else:
                        output_if = srv_soc
                        tgt_stream = self.send_data
                    tmp_data = r_obj.recv(4096)
                    tgt_stream[0] += tmp_data
                    if tmp_data:
                        output_if.send(tmp_data)
                        idle_count = 0
            if idle_count == max_idle_count:
                break
    
    # リクエスト取得関数
    def get_requestline(self):
        splited_requestline = self.requestline.split()
        # print "<< HTTP Request >>"
        # print splited_requestline, "\n"
        return splited_requestline

    # ヘッダ取得関数
    def get_header(self):
        splited_request_headers = str(self.headers).split("\r\n")
        # print "<< HTTP Request Header >>"
        # print splited_request_headers, "\n"
        return splited_request_headers
    
    # TCP接続関数
    def connect_tcp(self,netloc):
        # ホスト名とポートを分離 (何らかの理由でポート番号を変換できない場合空を返す)
        if ":" in netloc:
            (server_host_name, server_target_port) = tuple(netloc.split(":"))
            try:
                server_target_port = int(server_target_port)
            except:
                print "Invalid request port"
                return ""
        else:
            (server_host_name, server_target_port) = (netloc,80)
        
        # TCP接続開始
        tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tunnel.connect((server_host_name, server_target_port))
        except socket.error,arg:
            try:
                msg = arg[1]
            except:
                msg = arg
            self.send_error(404,msg)
            return ""
        return tunnel
    
    # コールバック関数、上書き用
    def callback(self,ConnectionInfo):
        pass

    # handle_http_proxyを全てのmethodに対して呼び出す
    def do_GET(self):
        self.handle_http_proxy()
    
    def do_HEAD(self):
        self.handle_http_proxy()

    def do_POST(self):
        self.handle_http_proxy()

    def do_PUT(self):
        self.handle_http_proxy()

    def do_DELETE(self):
        self.handle_http_proxy()

    def do_CONNECT(self):
        self.handle_https_proxy()

    def do_OPTIONS(self):
        self.handle_http_proxy()

    def do_TRACE(self):
        self.handle_http_proxy()

class HTTPProxy(object):
    class ThreadedHTTPProxy(ThreadingMixIn, HTTPServer):
        pass

    def __init__(self,address = ("",80),Handler = BaseHTTPRequestHandler):
        self.proxy = self.ThreadedHTTPProxy(address,Handler)

    def serve_forever(self):
        self.proxy.serve_forever()

# 接続情報を保存するクラス
class ConnectionInfo:
    def __init__(self):
        self.request = ""
        self.request_header = ""
        self.request_body = ""
        self.response = ""
        self.response_header = ""
        self.response_body = ""

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            port = 80
    else:
        port = 80

    server = HTTPProxy(("",port), ProxyHandler)
    print "Starting server in " + str(port)
    server.serve_forever()