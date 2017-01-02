# Python2.7 MultiProxyTool - LINUX ONLY

THIS TOOL IS ONLY FOR EDUCATIONAL PURPOSE!
IT IS IN AN ALPHA VERSION, THERE ARE MANY CRASHES AND BUGS!

# General Info
I'm not a pro python programer so expect some bugs and crashes. I hope 
some of you want to contribute to the project.


# TO-DOs
ARPPOISONING: 1.) Implement functionality with SSL (port 443) and SSLSTRIP

JSINJECTOR: 1.) A more reliable method to inject code dynamically.
            2.) Some more premade scripts.

SSLSTRIP:   1.) Improvement in stability
            

Overall better performance. Like shutting down running thread and reopening
ports after the program closed.


# Description
This is a man in the middle proxy. It is used to capture traffic
between computer without the knowing of them.


# Functions
REDIRECTER  => redirect every request to a given webpage or to your
			   own HTML code.
			  
JSINJECTOR  => injects javascript into the html code. Formstealer is one
			   preset script which can steal username and password and
			   send it to your database. The formstealer is very buggy
			   at the moment, so use it at your own risk.
			  
ARPPOISONER => Infects the network, so that the traffic of a given victim
			   is redirected to the proxy. (only http atm)
			   
SSLSTRIP    => Strip the secure HTTPS connections to a HTTP connection. Atm not supported
               with ARPPOISONING!


# How-To
To start the proxy you need to modify the config.json. You can create
new config files for your needs.

After you setup the config file you can start the proxy with:

(sudo) python Main.py config.json 

When you want to use the ARPPOISONER you need to start the tool
with root privilegs-

