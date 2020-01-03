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

#access_token = 'access-development-f93761be-3fd8-4cda-a5b4-bf6c7694c6b4'

PLAID_CLIENT_ID = '5d48d18f55135b001480ac71'
PLAID_SECRET = 'a9689bc3741c8630fad62c68dd2d10'
PLAID_PUBLIC_KEY = '34b103561ddb1fb432f5b922f4cc67'

PLAID_ENV = 'development'

client = plaid.Client(client_id = PLAID_CLIENT_ID, secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY, environment=PLAID_ENV, api_version='2019-05-29')


@app.route("/create_public_token", methods=['GET'])
def create_public_token():
    access_token = 'access-development-f93761be-3fd8-4cda-a5b4-bf6c7694c6b4'
    # Create a one-time use public_token for the Item.
    # This public_token can be used to initialize Link
    # in update mode for the user.
    response = client.Item.public_token.create(access_token)
    return jsonify(response)
	
if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 5000))
