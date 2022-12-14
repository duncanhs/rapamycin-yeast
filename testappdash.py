# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 12:17:37 2022

@author: hduncan
"""

# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask
from dash import Dash
import dash_html_components as html

# Flask constructor takes the name of
# current module (__name__) as argument.
#app = Flask(__name__)

server = Flask(__name__)

from werkzeug.middleware.proxy_fix import ProxyFix

server.wsgi_app = ProxyFix(
    server.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

@server.route('/')
# ‘/’ URL is bound with hello_world() function.

def hello_world():
	return 'Hello World but different'


app = Dash(__name__,
           server = server,
           #routes_pathname_prefix = "/dash"
           #suppress_callback_exceptions = True
           )

app.layout = html.Div(id = "This is the Dash app")

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.

# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.server.run(
        debug = True,
        host='0.0.0.0',
        port=8080
         )
