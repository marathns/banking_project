import base64
import os
import datetime
import plaid
import json
import time
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)

PLAID_ENV = 'development'
PLAID_PUBLIC_KEY = '34b103561ddb1fb432f5b922f4cc67'
PLAID_PUBLIC_TOKEN = 'public-development-089a34a5-8157-4b7c-abe3-380187a05a4e'

@app.route('/update')
def index():
  return render_template(
    'update_link.html',
	plaid_env = PLAID_ENV,
	plaid_public_key = PLAID_PUBLIC_KEY,
	plaid_public_token = PLAID_PUBLIC_TOKEN)
	
if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5000))
