import sys
import json

class ConfigParser:
    def __init__(self, config_file):
        self._config_file = config_file
        self._data = None

    def parseConfigFile(self):

        try:
            with open(self._config_file, "r") as json_data_files:
                data = json.load(json_data_files)
        except Exception:
            print "[-] Error with opening the config file! Exiting..."
            sys.exit(-3)

        self._data = data
        return data

    def printConfiguration(self):
        print "[*] Proxy Settings"
        print "[*] IP: " + str(self._data["proxy"]["ip"])
        print "[*] PORT HTTP: " + str(self._data["proxy"]["portHTTP"])
        print "[*] PORT SSL: " + str(self._data["proxy"]["portSSL"])
        print "[*] -----------------------------------"
        print "[*] Feature Settings"
        print "[*] HTTP/1.0: " + str(self._data["features"]["http10"])
        print "[*] ENCODING: " + str(self._data["features"]["encoding"])
        print "[*] NO COOKIES: " + str(self._data["features"]["nocookies"])
        print "[*] Favicon: " + str(self._data["features"]["favicon"])
        print "[*] -----------------------------------"
        print "[*] Function Settings"
        print "[*] ARP: " + str(self._data["functions"]["arp"])
        print "[*] REDIRECT TO: " + str(self._data["functions"]["redirectto"])
        print "[*] REDIRECT OWN: " + str(self._data["functions"]["redirectown"])
        print "[*] FORMSTEALER: " + str(self._data["functions"]["formstealer"])
        print "[*] SSLSTRIP: " + str(self._data["functions"]["sslstrip"])
        print "[*] -----------------------------------\n"
