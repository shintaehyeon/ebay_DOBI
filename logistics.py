import requests
import json

class LogisticsManager:
    def __init__(self, ebay_token, fedex_token, env='sandbox'):
        self.ebay_token = ebay_token
        self.fedex_token = fedex_token
        self.ebay_base_url = "https://api.sandbox.ebay.com/sell/fulfillment/v1" if env == 'sandbox' else "https://api.ebay.com/sell/fulfillment/v1"
        self.fedex_base_url = "https://apis-sandbox.fedex.com" if env == 'sandbox' else "https://apis.fedex.com"
        self.ebay_headers = {
            'Authorization': f'Bearer {self.ebay_token}',
            'Content-Type': 'application/json'
        }
        self.fedex_headers = {
            'Authorization': f'Bearer {self.fedex_token}',
            'Content-Type': 'application/json'
        }

    def get_ebay_orders(self):
        """Fetches orders that are paid but not yet shipped"""
        url = f"{self.ebay_base_url}/order?filter=orderfulfillmentstatus:%7BNOT_STARTED%7CPARTIAL%7D"
        response = requests.get(url, headers=self.ebay_headers)
        return response.json()

    def create_fedex_shipment(self, order_details):
        """
        Creates a shipment via FedEx and returns label data.
        This is a simplified example; actual FedEx API requires specific data mapping.
        """
        url = f"{self.fedex_base_url}/ship/v1/shipments"
        # Mapping eBay order_details to FedEx shipment structure would go here
        payload = {
            "labelResponseOptions": "URL_ONLY",
            "requestedShipment": {
                "shipper": { "contact": { "personName": "Seller Name" }, "address": { "streetLines": ["123 Seller St"], "city": "City", "stateOrProvinceCode": "ST", "postalCode": "12345", "countryCode": "US" } },
                "recipients": [{ "contact": { "personName": "Buyer Name" }, "address": { "streetLines": ["456 Buyer Rd"], "city": "Town", "stateOrProvinceCode": "BT", "postalCode": "67890", "countryCode": "US" } }],
                "shipTimestamp": "2023-10-27T10:00:00Z",
                "serviceType": "FEDEX_GROUND",
                "packagingType": "YOUR_PACKAGING",
                "pickupType": "CONTACT_FEDEX_TO_SCHEDULE",
                "shippingChargesPayment": { "paymentType": "SENDER" },
                "labelSpecification": { "labelFormatType": "COMMON2D", "imageType": "PDF" },
                "requestedPackageLineItems": [{ "weight": { "units": "LB", "value": 1.0 } }]
            },
            "accountNumber": { "value": "YOUR_FEDEX_ACCOUNT" }
        }
        response = requests.post(url, headers=self.fedex_headers, data=json.dumps(payload))
        return response.json()

    def update_ebay_tracking(self, order_id, tracking_number, carrier='FedEx'):
        """Uploads tracking information to eBay"""
        url = f"{self.ebay_base_url}/order/{order_id}/shipping_fulfillment"
        data = {
            "trackingNumber": tracking_number,
            "shippingCarrierCode": carrier,
            "lineItems": [] # Can be empty to fulfill all items
        }
        response = requests.post(url, headers=self.ebay_headers, data=json.dumps(data))
        return response.status_code
