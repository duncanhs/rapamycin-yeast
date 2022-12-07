# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 11:09:10 2022

@author: hduncan
"""
from dash import Dash
import dash_html_components as html


app = Dash(
    __name__,
    routes_pathname_prefix='/dash/'
)

app.layout = html.Div(id='example-div-element')


if __name__ == '__main__':
    app.run_server(debug=True)