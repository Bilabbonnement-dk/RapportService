"""
    Rapport Service:
    Håndterer...
"""

from flask import Flask, jsonify, request, make_response
import requests

app = Flask(__name__)



app.run(debug=True, host='0.0.0.0')