import os
from dotenv import load_dotenv
from auth import EBayAuth, FedExAuth
from listing import ListingManager
from repricer import Repricer
from logistics import LogisticsManager

load_dotenv()

def main():
    # 1. Initialize Auth
    ebay_auth = EBayAuth(
        os.getenv('EBAY_CLIENT_ID'),
        os.getenv('EBAY_CLIENT_SECRET'),
        os.getenv('EBAY_REDIRECT_URI'),
        env=os.getenv('EBAY_ENV', 'sandbox')
    )
    
    fedex_auth = FedExAuth(
        os.getenv('FEDEX_CLIENT_ID'),
        os.getenv('FEDEX_CLIENT_SECRET'),
        env=os.getenv('FEDEX_ENV', 'sandbox')
    )

    # Note: In a real app, you'd need to handle the initial browser-based OAuth consent
    # and store the refresh token. For this demo, we assume we have an access token.
    ebay_token = "YOUR_STORED_EBAY_TOKEN"
    fedex_token = fedex_auth.get_access_token().get('access_token')

    # 2. Initialize Managers
    listing_mgr = ListingManager(ebay_token, env=os.getenv('EBAY_ENV', 'sandbox'))
    repricer = Repricer(ebay_token, listing_mgr, env=os.getenv('EBAY_ENV', 'sandbox'))
    logistics = LogisticsManager(ebay_token, fedex_token, env=os.getenv('EBAY_ENV', 'sandbox'))

    print("--- eBay Automation Tool Started ---")

    # Example: Reprice an item
    # repricer.auto_adjust_price("SKU-123", "Keyword", min_price=10.0)

    # Example: Check for new orders
    # orders = logistics.get_ebay_orders()
    # print(f"Found {len(orders.get('orders', []))} new orders.")

if __name__ == "__main__":
    main()
