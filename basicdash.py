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
from dash import Dash
import flask
from dash import html

server = flask.Flask(__name__)
app = Dash(__name__, server=server, url_base_pathname='/')
app.layout = html.Div([html.H1('This Is head',style={'textAlign':'center'})])

@server.route("/dash")
def MyDashApp():
    return app.index()

from waitress import serve

if __name__ == '__main__':
    # app.run_server(debug=True)
    serve(app.server, host="0.0.0.0", port=8050)