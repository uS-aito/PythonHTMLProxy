#coding: utf-8
import SimpleHTTPServer
import threading
import BaseHTTPServer
import select
import socket
import SocketServer
import urlparse
import urllib2
import os
import fileinput

Thread = threading.Thread

class HttpdThread(Thread):
	def __init__(self):
		self.httpd = Httpd( ("" ,8080), ProxyServer ) 
		Thread.__init__(self)
	def run(self):
		self.httpd.serve_forever()
		pass
	def stop(self):
		self.httpd.server_close()
		pass

class Httpd(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
	pass


class ProxyServer(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_CONNECT(self):
		self.do_GET()
	def do_GET(self):
		code = self.header()
		if( code < 300 ):
			self.wfile.write( self.read() )
	def do_POST(self):
		self.do_GET()
	def do_HEAD(self):
		self.do_GET()
	def _docBase(self):
		return os.path.abspath(os.path.curdir)
	def _hasLocalFile(self):
		return os.path.lexists( self._localOverridePath() )
	def _localOverridePath(self):
		parsed = urlparse.urlparse(self.path)
		return (os.path.abspath(os.path.curdir)
				+ os.path.sep + "local"
				+ os.path.sep+parsed[1]
				+ parsed[2].replace("/", os.path.sep))
	def _localCachePath(self):
		parsed = urlparse.urlparse(self.path)
		return (os.path.abspath(os.path.curdir)
				+ os.path.sep + "cache"
				+ os.path.sep+parsed[1]
				+ parsed[2].replace("/", os.path.sep))
	def _readLocalFile(self):
		f = None
		try:
			f =file( self._localOverridePath() )
		finally:
			return f
	def _writeLocalCache(self,content):
		try:
#			if mkdirs in os :
#				os.mkdirs( os.path.dirname(self._localOverridePath()) )
#			elif makedirs in os :
				os.makedirs( os.path.dirname(self._localCachePath()) )
		except:
			""
		finally:
			import zlib
			try:
				content = zlib.decompress(content)
			except:
				""
			try:
				if self.res.info()["Content-type"].find("text") != -1 :
					mode = "w"
				else:
					mode = "wb"
				f = file( self._localCachePath(), mode )
				f.write( content )
				f.close()
			except:
				""
		return True
	def _makeLocalOverrideDir(self):
		try:
#			if mkdirs in os :
#				os.mkdirs( os.path.dirname(self._localOverridePath()) )
#			elif makedirs in os :
				os.makedirs( os.path.dirname(self._localOverridePath()) )
		except:
			""
		finally:
			return True
	def read(self):
		content = self._readLocalFile()
		if( content ):
			return content.read()
		else:
			self._makeLocalOverrideDir()
			data = self.res.read()
			self._writeLocalCache(data)
			return data
			
	def header(self):
		req = urllib2.Request( self.path )
		print self.path
		for x in self.headers:
			req.add_header( x, self.headers.getheader(x) )
		code = "404"
		hdr  = None
		try:
			res  = urllib2.urlopen(req)
			code = res.code
			hdr  = res.info()
			self.res = res
		except HTTPError,e :
			 code = e.code
			 hdr  = e.hdr
		finally:
			#response code
			self.send_response( code, self.responses[code] )
			for x in hdr:
				self.send_header( x, hdr[x] )
			self.end_headers()
			return code

thr = HttpdThread()
thr.start()
