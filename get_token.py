from auth import EBayAuth
import os
from dotenv import load_dotenv

load_dotenv()

def run_auth():
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    redirect_uri = os.getenv("EBAY_REDIRECT_URI")
    env = os.getenv("EBAY_ENV")

    auth = EBayAuth(client_id, client_secret, redirect_uri, env)
    
    # Define scopes for inventory and listing
    scopes = [
        "https://api.ebay.com/oauth/api_scope/sell.inventory",
        "https://api.ebay.com/oauth/api_scope/sell.marketing",
        "https://api.ebay.com/oauth/api_scope/sell.account",
        "https://api.ebay.com/oauth/api_scope/sell.fulfillment"
    ]
    
    auth_url = auth.get_authorization_url(scopes)
    
    print("\n" + "="*50)
    print("STEP 1: 아래 URL을 브라우저에 복사하여 접속하세요.")
    print("="*50)
    print(auth_url)
    print("="*50)
    print("\n로그인 후 주소창에 나오는 'code=' 뒤의 값을 복사해서 저에게 알려주세요!")

if __name__ == "__main__":
    run_auth()
