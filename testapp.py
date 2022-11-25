# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 12:17:37 2022

@author: hduncan
"""

from flask import Flask, render_template
app = Flask(__name__)
@app.route('/')
def home():
  return render_template('home.html')
if __name__ == '__main__':
  app.run()