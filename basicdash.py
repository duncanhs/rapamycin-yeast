# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:09:10 2022

@author: hduncan
"""

# import dash
# import dash_html_components

# app = dash.Dash(__name__)
# app.config.suppress_callback_exceptions = True
# app.config.update(
# 	{
# 		'routes_pathname_prefix': '',
# 		'requests_pathname_prefix': ''
# 	}
# )
# server = app.server
# app.layout = dash_html_components.Div(
# 	[
# 		dash_html_components.H1("Hello Dash World")
# 	]
# )

# if __name__ == '__main__':
#     app.run_server()

from dash import Dash
from werkzeug.wsgi import DispatcherMiddleware
import flask
from werkzeug.serving import run_simple

server = flask.Flask(__name__)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashboard' )

@server.route('/')
@server.route('/hello')
def hello():
    return 'hello world!'

@server.route('/dashboard')
def render_dashboard():
    return flask.redirect('/dash1')



app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server
})

run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)