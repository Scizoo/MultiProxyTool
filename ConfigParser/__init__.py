import sys
import json

class ConfigParser:
    def __init__(self, config_file):
        self._config_file = config_file


    def parseConfigFile(self):

        try:
            with open(self._config_file, "r") as json_data_files:
                data = json.load(json_data_files)
        except Exception:
            print "[-] Error with opening the config file! Exiting..."
            sys.exit(-3)

        return data
