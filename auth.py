import requests
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

class EBayAuth:
    def __init__(self, client_id, client_secret, redirect_uri, env='sandbox'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.env = env
        self.token_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token" if env == 'sandbox' else "https://api.ebay.com/identity/v1/oauth2/token"
        self.auth_url = "https://auth.sandbox.ebay.com/oauth2/authorize" if env == 'sandbox' else "https://auth.ebay.com/oauth2/authorize"

    def get_authorization_url(self, scopes):
        """Step 1: Generate Authorization URL for User Consent"""
        from urllib.parse import urlencode
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes)
        }
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code_for_token(self, auth_code):
        """Step 3: Exchange Authorization Code for Access Token"""
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri
        }
        response = requests.post(self.token_url, headers=headers, data=data)
        return response.json()

    def refresh_access_token(self, refresh_token):
        """Step 4: Refresh Access Token using Refresh Token"""
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        response = requests.post(self.token_url, headers=headers, data=data)
        return response.json()

class FedExAuth:
    def __init__(self, client_id, client_secret, env='sandbox'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://apis-sandbox.fedex.com/oauth/token" if env == 'sandbox' else "https://apis.fedex.com/oauth/token"

    def get_access_token(self):
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        response = requests.post(self.token_url, data=data)
        return response.json()
