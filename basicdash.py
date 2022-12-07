# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:09:10 2022

@author: hduncan
"""
from dash import Dash
import dash_html_components as html
from werkzeug.middleware.proxy_fix import ProxyFix

app = Dash(
    __name__,
    routes_pathname_prefix='/dash/'
)

app.layout = html.Div(id='example-div-element')

app.server.wsgi_app = ProxyFix(
    app.server.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


if __name__ == '__main__':
    app.run_server(debug=True)