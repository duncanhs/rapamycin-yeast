# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 12:17:37 2022

@author: hduncan
"""

# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)


# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.

def hello_world():
	return 'Hello World'

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run(port = 8000)
    
    

from werkzeug.middleware.proxy_fix import ProxyFix
# App is behind one proxy that sets the -For and -Host headers.
app = ProxyFix(app, x_for=1, x_host=1)


