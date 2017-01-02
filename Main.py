from Proxy import Client
from ARPPoisoning import ARPPoisoning
from ConfigParser import ConfigParser
from Functions import Functions
import threading
import socket, ssl
import sys
import os
import re
import time


class ServerThread(threading.Thread):
    def __init__(self, address, tools, configsettings):
        threading.Thread.__init__(self)
        self._address = address
        self._tools = tools
        self._config = configsettings
        self.isRunning = True
        self._stop = threading.Event()

    def setup(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind(self._address)
        except socket.error as msg:
            return False, msg

        try:
            with open("/proc/sys/net/core/somaxconn", 'r') as f:
                backlog = int(f.readline())
        except Exception:
            backlog = 5

        if backlog > 0:
            self.server.listen(backlog)
        else:
            self.server.listen(5)

        print "[*] Backlog set to: " + str(backlog)


        return True, "Setup completed."

    def run(self):
        clients = []
        tools = Functions() #maybe change to global
        print "Server starts listening on " + str(self._address)
        while self.isRunning:
            try:
                conn, addr = self.server.accept()
                client = Client(conn, self._config, tools)
                clients.append(client)
                client.start()
            except socket.error as msg:
                print msg
                continue


        print "Waiting for threads to shutdown correct"
        [t.stop() for t in clients]
        #[t.join() for t in clients]
        print "Done! Thank you"
        #self.server.close()


    def stop(self):
        self.isRunning = False
        self._stop.set()
        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()




def startProxy(ip, portHTTP, portSSL, arp_flag, config):
    arppoisoning = None
    if arp_flag:
        print "[*] You started a ARP poisoning request\n" \
              "[*] This feature is only for educational purpose!\n" \
              "[*] Only use this on your private network!\n" \
              "[*] ----------------------------------------------\n" \
              "[*] Root is needed! Checkig for root now.....\n"

        if checkRoot() is False:
            print "[-] No ROOT privilges found! Exiting..."
            sys.exit(-1)
        else:
            print "[+] Root found! Moving on.\n"

        arppoisoning = ARPPoisoning(ip, portHTTP, portSSL)
        arpstarted = arppoisoning.setup()
        if not arpstarted:
            print "\n[-] Setup interrupted! Exiting..."
            sys.exit(-1)

        arppoisoning.start()

    # Features initialization
    tools = Functions()

    httpServer = ServerThread((ip, portHTTP), tools, config)
    status1 = httpServer.setup()

    if portHTTP != portSSL:
        sslServer = ServerThread((ip, portSSL), tools, config)
        status2 = sslServer.setup()
    else:
        status2 = True, "Not used"

    if not status1[0] or not status2[0]:
        print "HTTP SERVER: " + str(status1[1])
        print "SSL  SERVER: " + str(status2[1])
        sys.exit(-1)

    httpServer.start()
    if portHTTP != portSSL:
        sslServer.start()

    print "[+] Running..."

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "[*] Stopping..."
        httpServer.stop()
        if portHTTP != portSSL:
            sslServer.stop()
        if arppoisoning is not None and arppoisoning.isActive:
            arppoisoning.stop()

    httpServer.join()
    if portHTTP != portSSL:
        sslServer.join()

    print "[+] End Program"


def checkRoot():
    if not os.geteuid() == 0:
        return False

    return True

if __name__ == '__main__':
    if len(sys.argv) is not 2:
        print "[-] Please specify a *.json config file!"
        sys.exit(-2)

    # Test config parse
    cp = ConfigParser(sys.argv[1])
    config = cp.parseConfigFile()
    cp.printConfiguration()
    # ----------------------- #
    try:
        arp_flag = int(config["functions"]["arp"])
    except Exception:
        print "[-] Config error functions/arp. Please check! Exiting..."
        sys.exit(-1)

    ip = config["proxy"]["ip"]
    pat = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    test = pat.match(ip)

    if not test:
        print("Wrong ip format! Please check config file. Exiting...")
        sys.exit(-1)

    try:
        portHTTP = int(config["proxy"]["portHTTP"])
        portSSL = int(config["proxy"]["portSSL"])
    except:
        print "Port must be a number between 1-65535"
        sys.exit(-3)

    if portHTTP < 1 or portHTTP > 65535:
        print "Port must be a number between 1-65535"
        sys.exit(-3)

    if portSSL < 1 or portSSL > 65535:
        print "Port must be a number between 1-65535"
        sys.exit(-3)

    startProxy(ip, portHTTP, portSSL, arp_flag, config)
