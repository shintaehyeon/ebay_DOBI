import requests
import json

class ListingManager:
    def __init__(self, auth_token, env='sandbox'):
        self.auth_token = auth_token
        self.base_url = "https://api.sandbox.ebay.com/sell/inventory/v1" if env == 'sandbox' else "https://api.ebay.com/sell/inventory/v1"
        self.headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json',
            'Content-Language': 'en-US'
        }

    def create_or_replace_inventory_item(self, sku, product_data):
        """Creates or updates an inventory item (SKU-based)"""
        url = f"{self.base_url}/inventory_item/{sku}"
        response = requests.put(url, headers=self.headers, data=json.dumps(product_data))
        return response.status_code, response.json() if response.status_code != 204 else "Success"

    def bulk_create_offers(self, offers):
        """Bulk creates offers for inventory items"""
        url = f"{self.base_url}/bulk_create_offer"
        response = requests.post(url, headers=self.headers, data=json.dumps({'requests': offers}))
        return response.json()

    def bulk_publish_offers(self, offer_ids):
        """Bulk publishes created offers to make them live listings"""
        url = f"{self.base_url}/bulk_publish_offer"
        data = {'offerIds': offer_ids}
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return response.json()

    def get_inventory_items(self, limit=10, offset=0):
        """Retrieves a list of inventory items"""
        url = f"{self.base_url}/inventory_item?limit={limit}&offset={offset}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def bulk_update_price_quantity(self, updates):
        """Updates price and quantity for multiple items at once"""
        url = f"{self.base_url}/bulk_update_price_quantity"
        response = requests.post(url, headers=self.headers, data=json.dumps({'requests': updates}))
        return response.json()
