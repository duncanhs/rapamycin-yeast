# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 15:48:10 2022

@author: hduncan
"""

from werkzeug.middleware.proxy_fix import ProxyFix
# App is behind one proxy that sets the -For and -Host headers.
app = ProxyFix(app, x_for=1, x_host=1)