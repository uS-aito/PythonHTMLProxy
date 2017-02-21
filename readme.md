# PythonHTTPProxy

PythonHTTPProxyはPythonによるプロキシモジュールです。
PythonHTTPProxyはPython2.x環境で動作し、モジュール単体で動作し、他のPythonoプログラムにimportして利用することもできます。  
```
# python PythonHTTPProxy.py 80
Starting Server in 80
```
```
import PythonHTTPProxy
...
proxy = PythonHTTPProxy.HTTPProxy(("",port))
proxy.serve_forever()
```
## Description
PythonHTTPProxyはL5レベルで通信をトンネルするプロキシです。　　
マルチスレッドで動作し、すべてのHTTP1.1におけるメソッドをサポートしています。  
PythonHTTPProxyを介して行われた通信のリクエスト・レスポンスは全てバッファされているので、開発者はPythonHTTPProxyをimportすることで、通信の内容を利用するアプリケーションを開発できます。

## Development
PythonHTTPProxyを経由した通信の内容を保存するクラスは以下の通りです。
```
class ConnectionInfo:
    def __init__(self):
        self.request = ""
        self.request_header = ""
        self.request_body = ""
        self.response = ""
        self.response_header = ""
        self.response_body = ""
```
*request・response*変数はリクエストラインとレスポンスラインが保存されます。*request_header・response_header*は各ヘッダが、*request_body・response_body*は各ボディが保存されます。  
ConnectionInfoクラスは一連の通信が終了した(TCP通信がクローズした)タイミングで実行されるメソッド*callback*に引数として与えられます。
```
def callback(self,ConnectionInfo):
    pass
```
このメソッドはProxyHandlerを継承したクラスでオーバーライドされることを想定して定義されています。  
オーバーライドした*callback*メソッドを利用したプロキシを実行するには、ProxyHandlerを継承したクラスを引数としてHTTPProxyクラスのインスタンスを作成します。  
以下の例では、URLにgoogleを含む通信があった場合、HELLO GOOGLEと表示するcallbackメソッドを示します。
```
class AnotherProxyHandler(ProxyHandler):
    def callback(self,ConnectionInfo):
        if "google" in ConnectionInfo:
            print "HELLO GOOGLE"

proxy = PythonHTTPProxy.HTTPProxy(("",port),AnotherProxyHandler)
proxy.serve_forever()
```

## License
本ソフトウェアは[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)ライセンスに準じます。