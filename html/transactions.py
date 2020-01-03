from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os, sys, inspect
import json

app = Flask(__name__)


client_id = 'buftq4SN1h8k2nQaJFXXKrY0cjh7Bmj2vPGEYhZY'
client_secret = 'e5IvSl8UDkgasLQ4ymGlgN91NWk0rB5f4J7lOfwG'

authorization_base_url = 'https://secure.splitwise.com/api/v3.0/get_expenses'
token_url = 'https://secure.splitwise.com/oauth/token'


@app.route("/")
def demo():
    """Step 1: User Authorization.
    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    splitwise = OAuth2Session(client_id)
    authorization_url, state = splitwise.authorization_url(authorization_base_url)
    # print(authorization_url)
    session['oauth_state'] = state
    print(session['oauth_state'])
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.
    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    print(request.url)
    splitwise = OAuth2Session(client_id, state=session['oauth_state'])
    url = 'https://secure.splitwise.com/api/v3.0/get_expenses?response_type=code&client_id=buftq4SN1h8k2nQaJFXXKrY0cjh7Bmj2vPGEYhZY&state=J3CZNzRyrTLXOEb1MNOZS1Lqel9oPz'
    token = splitwise.fetch_token(token_url, client_secret=client_secret, authorization_response=url)

    session['oauth_token'] = token
    print(session['oauth_token'])
    return redirect(authorization_url)


@app.route("/expenses", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    splitwise = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(splitwise.get('https://secure.splitwise.com/api/v3.0/get_expenses').json())

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)
