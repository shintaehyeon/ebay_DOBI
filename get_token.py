from auth import EBayAuth
import os
from dotenv import load_dotenv, set_key

load_dotenv()

def run_auth():
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    redirect_uri = os.getenv("EBAY_REDIRECT_URI")
    env = os.getenv("EBAY_ENV")

    if not all([client_id, client_secret, redirect_uri]):
        print("❌ .env 파일에 EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_REDIRECT_URI를 먼저 설정해주세요.")
        return

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
    
    from urllib.parse import unquote
    auth_code = input("\nSTEP 2: 로그인 후 주소창의 'code=' 뒤에 있는 값을 입력하세요: ").strip()
    # URL Decoding if needed
    if "%" in auth_code:
        auth_code = unquote(auth_code)
    
    if auth_code:
        print("\n⏳ 토큰 교환 중...")
        token_data = auth.exchange_code_for_token(auth_code)
        
        if 'access_token' in token_data:
            access_token = token_data['access_token']
            # .env 파일 업데이트
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            set_key(env_path, "EBAY_ACCESS_TOKEN", access_token)
            
            print("\n✅ 성공! EBAY_ACCESS_TOKEN이 .env 파일에 저장되었습니다.")
            print(f"토큰 만료 시간: {token_data.get('expires_in')}초")
        else:
            print("\n❌ 토큰 교환 실패!")
            print(f"에러 정보: {token_data}")

if __name__ == "__main__":
    run_auth()
