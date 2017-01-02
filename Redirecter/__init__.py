from Functions import Functions

class Redirecter:
    def __init__(self):
        self._responseRedirect = 'HTTP/1.1 301 Moved Permanently\r\n' \
                                 'Location: URLPLACEHOLDER\r\n' \
                                 'Connection: close\r\n' \
                                 'Content-length: 0\r\n\r\n'

        self._responseDisplayOwnPage = 'HTTP/1.1 200 OK\r\n' \
                                       'Content-Length: LENGTHPLACEHOLDER\r\n' \
                                       'Content-Type: text/html\r\n' \
                                       'Connection: close\r\n\r\n' \
                                       'BODYPLACEHOLDER'

        self._tools = Functions()


    def redirectToURL(self, url, client, header):

            if type(url) is not str:
                print "URL must be a string"
                return False

            host = self._tools.getHostname(header)
            host2 = "http://" + host + "/"
            #print "[+] Hostname: " + str(host)

            if str(url) in host or str(url) in host2:
                #print "[*] Debug: Redirected site"
                return False

            self._responseRedirect = self._responseRedirect.replace("URLPLACEHOLDER", url)

            print "[*] Redirecting to url:\n" + str(self._responseRedirect)
            client.sendall(bytes(self._responseRedirect))

            return True

    def redirectDislpayOwnPage(self, file, client):
        try:
            # Load content which should be displayed
            with open(file, "r") as f:
                filecontent = f.readlines()

            content = ""
            for c in filecontent:
                content += c

            if content is "":
                return False

            self._responseDisplayOwnPage = self._responseDisplayOwnPage.replace("LENGTHPLACEHOLDER", str(len(content)))
            self._responseDisplayOwnPage = self._responseDisplayOwnPage.replace("BODYPLACEHOLDER", str(content))

            client.sendall(bytes(self._responseDisplayOwnPage))

            print "[+] Successfully send page to client!"

            return True
        except (OSError, IOError) as e:
            print "[-] " + str(e)
            return False
        except Exception:
            print "[-] Something went wrong..."
            return False
