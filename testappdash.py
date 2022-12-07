# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 12:17:37 2022

@author: hduncan
"""

# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask
from dash import Dash

# Flask constructor takes the name of
# current module (__name__) as argument.
#app = Flask(__name__)

# app = Dash(__name__,
#            #server = server,
#            suppress_callback_exceptions = True
#            )

app = Dash()

from werkzeug.middleware.proxy_fix import ProxyFix

app.server.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

server = app.server

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.

def hello_world():
	return 'Hello World but different'

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run_server(
        host='0.0.0.0',
        port=8080
         )