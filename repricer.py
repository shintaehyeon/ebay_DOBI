import requests
import json

class Repricer:
    def __init__(self, auth_token, listing_manager, env='sandbox'):
        self.auth_token = auth_token
        self.listing_manager = listing_manager
        self.base_url = "https://api.sandbox.ebay.com/buy/browse/v1" if env == 'sandbox' else "https://api.ebay.com/buy/browse/v1"
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        }

    def search_competitors(self, keyword):
        """Searches for similar items to find competitor prices"""
        url = f"{self.base_url}/item_summary/search?q={keyword}&limit=10"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('itemSummaries', [])
        return []

    def get_lowest_competitor_price(self, items):
        """Extracts the lowest price from a list of items"""
        prices = []
        for item in items:
            price_val = float(item.get('price', {}).get('value', 0))
            if price_val > 0:
                prices.append(price_val)
        return min(prices) if prices else None

    def auto_adjust_price(self, sku, keyword, min_price, undercut_amount=0.10):
        """
        Logic:
        1. Search competitors by keyword.
        2. Find lowest price.
        3. Undercut by undercut_amount.
        4. Ensure result is above min_price.
        5. Update eBay listing.
        """
        competitors = self.search_competitors(keyword)
        lowest_price = self.get_lowest_competitor_price(competitors)
        
        if lowest_price:
            new_price = max(lowest_price - undercut_amount, min_price)
            print(f"Lowest competitor: {lowest_price}, New price: {new_price}")
            
            update = {
                'sku': sku,
                'price': {
                    'value': str(new_price),
                    'currency': 'USD'
                }
            }
            return self.listing_manager.bulk_update_price_quantity([update])
        return "No competitors found"
