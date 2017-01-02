import re

DATASIZE = 8192


class Functions:
    def __init__(self):
        self.listOfChangesToHttp = []

    def HeaderChanger(self, header):
        pass

    def getHostname(self, header):
        if "CONNECT" in header:
            start = header.index("CONNECT ") + len("CONNECT ")
            end = header.index(" ", start)

            hostPort = header[start:end]
            hostname = hostPort.split(":")

            return hostname[0]

        start = header.index("Host: ") + len("Host: ")
        end = header.index("\r\n", start)
        hostPort = header[start:end]
        hostname = hostPort.split(":")

        return hostname[0]

    def changeAbsoluteToRelativeHostname(self, header):
        hostname = self.getHostname(header)

        fulldomain = "http://" + str(hostname)

        request = header.replace(fulldomain, "")

        return request

    def changeHTTP11to10(self, header):
        if "HTTP/1.1" in header:
            header = header.replace("HTTP/1.1", "HTTP/1.0")

        return header

    def changeEncoding(self, header):

        if "Accept-Encoding:" in header:
            start = header.index("Accept-Encoding: ") + len("Accept-Encoding: ")
            end = header.index("\r\n", start)

            encoding = header[start:end]
            header = header.replace(encoding, "")

        return header

    def changeConnectionType(self, header):
        if "Connection: keep-alive" in header:
            header = header.replace("Connection: keep-alive", "Connection: close")

        return header

    def changeResponseLinks(self, response):
        '''Im header auf Location: https:// kontrollieren'''
        if "Location: https://" in response:
            response = response.replace("Location: https://", "Location: http://")
            start = response.index("Location: http://") + len("Location: ")
            end = response.index("\r\n", start)
            self.listOfChangesToHttp.append(response[start:end])  # adding changed link to list

        '''Im body auf <a href="https:// kontrollieren'''
        if '<a href="https://' in response:
            # Find all https:// links
            l = re.findall('https://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(response))
            x = 0
            # replace links with http://
            for item in l:
                l[x] = item.replace("https://", "http://")

                # if not in list yet, safe it now to list
                if not any(l[x] in s for s in self.listOfChangesToHttp):
                    self.listOfChangesToHttp.append(l[x])

                x += 1

            response = response.replace('<a href="https://', '<a href="http://')

        return response

    def checkLinks(self, request):
        '''Check the GET request, when link is in the list, change it back to https'''
        getpost = ""

        if "GET " in self.getFirstLine(request):
            getpost = "GET "
        elif "POST " in self.getFirstLine(request):
            getpost = "POST "
        else:
            return request

        start = request.index(getpost) + len(getpost)
        end = request.index(" ", start)
        url = request[start:end]

        if any(url in s for s in self.listOfChangesToHttp):
            newurl = url.replace("http://", "https://")
            request = request.replace(url, newurl)

        return request

    def sslBuilder(self, request):
        '''Make a GET request to a CONNECT (SSL) request'''
        pass

    def noCookies(self, response):
        if "Set-Cookie:" in response:
            print("##### Deleting Set-Cookie #####")
            start = response.index("Set-Cookie: ")
            end = response.index("\r\n", start) + len("\r\n")
            cookie = response[start:end]
            response = response.replace(cookie, "")

        return response

    def getHeader(self, response):
        end = response.index("\r\n\r\n") + len("\r\n\r\n")
        header = response[0:end]

        return header

    def redirect(self, response):
        resp = response
        file = open("refresh.txt", "r")
        resp = file.read() + "\r\n\r\n"

        return resp

    def seperateHeaderBody(self, request):
        head = request.index("\r\n\r\n") + len("\r\n\r\n")
        b = request.index(head, "\r\n\r\n")
        header = request[0:head]
        body = request[head, b]

        req = [header, body]

        return req

    def getFirstLine(self, header):
        end = header.index("\r\n")
        first = header[:end]
        return first

    def changeFavIcon(self, request):
        if "Location: " in request:
            start = request.index("Location: ") + len("Location: ")
            end = request.index("\r\n")
            url = request[start:end]

            if "favicon.ico" in url:
                print("Fav Icon Found!")
                print("Changed: " + str(url) + " to ")
                newurl = "http://dchoa.org/images/icons/Lock.ico"
                print(str(newurl))
                request.replace(url, newurl)

        if "GET " in request[:4]:
            firstline = self.getFirstLine(request)
            if "favicon.ico" in firstline:
                start = firstline.index("GET ") + len("GET ")
                end = firstline.index(" ", start)
                url = firstline[start:end]
                print("Changed: " + str(url) + " to ")
                newurl = "http://dchoa.org/images/icons/Lock.ico"
                print(str(newurl))
                request.replace(url, newurl)

        return request

    def getRequest(self, s):
        req = ""
        while True:
            request = s.recv(DATASIZE)
            req += request

            # Wenn ende erreicht dann break
            if "\r\n\r\n" in req:
                break;

        return req

    def changeContentlength(self, header, length_to_add):
        if length_to_add is 0:
            return header, 0
        try:
            if "Content-Length: " in header:
                start = header.index("Content-Length: ") + len("Content-Length: ")
                end = header.index("\r\n", start)
                oldlength = int(header[start:end])
                newlength = oldlength + length_to_add
                headernew = header.replace(str(oldlength), str(newlength))
                return headernew, 1
        except Exception:
            return header, 0

        return header, 0
