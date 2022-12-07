# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:09:10 2022

@author: hduncan
"""

# import dash
# import dash_html_components

# app = dash.Dash(__name__, url_base_pathname= '/dash')
#app.config.suppress_callback_exceptions = True
# app.config.update(
#  	{
# 		'routes_pathname_prefix': '',
# 		'requests_pathname_prefix': ''
#  	}
# )
# server = app.server
# app.layout = dash_html_components.Div(
#  	[
# 		dash_html_components.H1("Hello Dash World")
#  	]
# )

# if __name__ == '__main__':
#     app.run_server()
#here are full codee
# from dash import Dash
# import flask
# from dash import html

# server = flask.Flask(__name__)
# app = Dash(__name__, server=server, url_base_pathname='/')
# app.layout = html.Div([html.H1('This Is head',style={'textAlign':'center'})])

# @server.route("/dash")
# def MyDashApp():
#     return app.index()

# from waitress import serve

# if __name__ == '__main__':
#     # app.run_server(debug=True)
    # serve(app.server, host="0.0.0.0", port=8050)
    
from flask import Flask
from dash import Dash, html, dcc

app = Flask(__name__)
dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/instances/home/scetorprd/htdocs/rapamycin-yeast/'
)

app.layout = html.Div(id='dash-container')

# @server.route("/dash")
# def my_dash_app():
#     return app.index()

# @server.route('/')
# # ‘/’ URL is bound with hello_world() function.

# def hello_world():
# 	return 'Hello World but different'

@app.route("/")
def my_dash_app():
    #return dash_app.index()
    return 'Hello world again'

if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run(
        host='0.0.0.0',
        port=8080
         )
