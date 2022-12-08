# -*- coding: utf-8 -*-
"""
Created on Thu Dec  8 11:09:22 2022

@author: hduncan
"""

workers = 4
bind = '127.0.0.1:8080'
umask = 0o007
reload = True
accesslog = 'log_gunicorn_access.txt'
errorlog = 'log_gunicorn_error.txt'