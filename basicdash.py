# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:09:10 2022

@author: hduncan
"""

# import dash
# import dash_html_components

# app = dash.Dash(__name__, url_base_pathname= '/dash')
app.config.suppress_callback_exceptions = True
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
import flask
import dash

server = flask.Flask(__name__)

app = dash.Dash(__name__,
               url_base_pathname = '/dash',
               server = server)

@server.route('/dash')
def hello():
    return 'Hello, World!'
