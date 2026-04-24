import requests
import json

class ListingManager:
    """
    Manages eBay listings using the modern RESTful Inventory API.
    Flow: Create Inventory Item -> Create Offer -> Publish Offer.
    """
    def __init__(self, auth_token, env='sandbox'):
        self.auth_token = auth_token
        if env == 'sandbox':
            self.base_url = "https://api.sandbox.ebay.com/sell/inventory/v1"
        else:
            self.base_url = "https://api.ebay.com/sell/inventory/v1"

    def create_or_replace_inventory_item(self, sku, item_data):
        """
        Step 1: Create or update an inventory item (the product itself).
        """
        url = f"{self.base_url}/inventory_item/{sku}"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "Content-Language": "en-US"
        }
        
        # Mapping our AI data to eBay format
        payload = {
            "availability": {
                "shipToLocationAvailability": {"quantity": 10}
            },
            "condition": "NEW",
            "product": {
                "title": item_data.get("title", "No Title"),
                "description": item_data.get("description", "No Description"),
                "imageUrls": [item_data.get("image_url", "")]
            }
        }
        
        print(f"Creating/Updating Inventory Item: {sku}...")
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code in [200, 204]:
            print("Successfully updated inventory item.")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

    def create_offer(self, sku, price, marketplace_id='EBAY_US'):
        """
        Step 2: Create an offer for the inventory item.
        This defines price, quantity, and market.
        """
        url = f"{self.base_url}/offer"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "Content-Language": "en-US"
        }
        
        payload = {
            "sku": sku,
            "marketplaceId": marketplace_id,
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "categoryId": "31387", # Example: Jewelry & Watches (Need to be dynamic)
            "listingPolicies": {
                "fulfillmentPolicyId": "YOUR_FULFILLMENT_POLICY_ID",
                "paymentPolicyId": "YOUR_PAYMENT_POLICY_ID",
                "returnPolicyId": "YOUR_RETURN_POLICY_ID"
            },
            "pricingSummary": {
                "price": {"value": str(price), "currency": "USD"}
            }
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 201:
            offer_id = response.json().get("offerId")
            print(f"Offer created successfully. Offer ID: {offer_id}")
            return offer_id
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def publish_offer(self, offer_id):
        """
        Step 3: Publish the offer to make it live on eBay.
        """
        url = f"{self.base_url}/offer/{offer_id}/publish"
        headers = {
            "Authorization": f"Bearer {self.auth_token}"
        }
        
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            listing_id = response.json().get("listingId")
            print(f"Listing published! Listing ID: {listing_id}")
            return listing_id
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

if __name__ == "__main__":
    # Actual test with token
    # manager = ListingManager(auth_token="YOUR_TOKEN")
    # manager.create_or_replace_inventory_item("TEST_SKU_001", {"title": "Test Item"})
    pass
