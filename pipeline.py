import os
from sourcing import SourcingEngine
from ai_studio import AIStudio
from listing import ListingManager
from database import DatabaseManager
import requests

class AutomationPipeline:
    def __init__(self):
        # 환경 변수 직접 로드
        ebay_token = os.getenv("EBAY_ACCESS_TOKEN", "YOUR_TOKEN")
        remove_bg_key = os.getenv("REMOVE_BG_KEY")
        
        self.sourcing_engine = SourcingEngine()
        self.ai_studio = AIStudio(remove_bg_key=remove_bg_key)
        self.listing_manager = ListingManager(auth_token=ebay_token)
        self.db = DatabaseManager()
        
        self.static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "static")
        if not os.path.exists(self.static_dir):
            os.makedirs(self.static_dir)

    def run_full_pipeline(self, url, user_id=1, do_list=False):
        """
        Full workflow with Database logging for trend analysis.
        """
        # 1. Scrape data
        product_data = self.sourcing_engine.scrape_product(url)
        if not product_data:
            self.db.log_activity(user_id, url, "Unknown", "Unknown", 0) # Log failed attempt
            raise Exception("상품 정보를 수집할 수 없습니다.")

        # 2. Log success to DB for trend analytics (Quarterly reports data)
        self.db.log_activity(
            user_id=user_id,
            url=url,
            store_name=product_data['source'],
            category=product_data.get('category', 'General'),
            price=product_data['price']
        )

        # 3. AI Picking & Washing (Free using rembg)
        image_urls = product_data.get('image_urls', [])
        best_img_url = self.ai_studio.pick_best_image(image_urls)
        
        temp_original = os.path.join(self.static_dir, "temp_original.jpg")
        temp_cleaned = os.path.join(self.static_dir, "temp_cleaned.jpg")

        img_data = requests.get(best_img_url).content
        with open(temp_original, 'wb') as handler:
            handler.write(img_data)

        # Background Removal
        success = self.ai_studio.remove_background(temp_original, temp_cleaned)
        processed_image_rel = "static/" + ("temp_cleaned.jpg" if success else "temp_original.jpg")

        # 4. Generate AI Metadata
        ai_metadata = self.ai_studio.analyze_product_with_ai(temp_original)
        
        result_data = {
            **ai_metadata,
            "title": product_data['title'],
            "original_price": product_data['price'],
            "image_path": processed_image_rel,
            "source": product_data['source']
        }

        if do_list:
            import time
            sku = f"KGOODS_{int(time.time())}"
            print(f"📦 eBay Sandbox API와 통신하여 재고(Inventory)에 상품({sku})을 등록합니다...")
            
            # eBay 제목 길이 제한 처리 (1~80자)
            valid_title = result_data.get("title", "")
            if not valid_title:
                valid_title = "K-Goods Premium Product"
            if len(valid_title) > 80:
                valid_title = valid_title[:77] + "..."

            # eBay Sandbox Inventory API 호출
            item_data = {
                "title": valid_title,
                "description": result_data["description"],
                "image_url": "https://i.ebayimg.com/images/g/example/s-l500.jpg" # API 테스트용 가짜 이미지 URL
            }
            self.listing_manager.create_or_replace_inventory_item(sku, item_data)

        return result_data
