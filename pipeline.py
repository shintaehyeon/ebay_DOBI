import os
from sourcing import SourcingEngine
from ai_studio import AIStudio
from listing import ListingManager
from database import DatabaseManager
import requests
import shutil

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

    def run_full_pipeline(self, url, user_id=1, do_list=False, skip_ai=False):
        """
        Full workflow with Database logging for trend analysis.
        """
        # 1. Scrape data
        product_data = self.sourcing_engine.scrape_product(url)
        if not product_data:
            self.db.log_activity(user_id, url, "Unknown", "Unknown", 0)
            raise Exception("상품 정보를 수집할 수 없습니다.")

        # 3. AI Picking & Washing
        image_urls = product_data.get('image_urls', [])
        best_img_url = self.ai_studio.pick_best_image(image_urls)
        
        temp_original = os.path.join(self.static_dir, "temp_original.jpg")
        temp_cleaned = os.path.join(self.static_dir, "temp_cleaned.jpg")

        img_data = requests.get(best_img_url).content
        with open(temp_original, 'wb') as handler:
            handler.write(img_data)

        # Background Removal (Skip if skip_ai is True)
        if not skip_ai:
            success = self.ai_studio.remove_background(temp_original, temp_cleaned)
            processed_image_rel = "static/temp_cleaned.jpg" if success else "static/temp_original.jpg"
        else:
            processed_image_rel = "static/temp_original.jpg"

        # 4. Generate AI Metadata
        ai_metadata = self.ai_studio.analyze_product_with_ai(temp_original)
        
        result_data = {
            **ai_metadata,
            "title": product_data['title'],
            "original_price": str(round(float(product_data['price'].replace(',', '')) / 1350 * 1.5, 2)), # Auto-convert with margin
            "image_path": processed_image_rel,
            "source": product_data['source']
        }
        return result_data

    def run_image_pipeline(self, image_paths, do_list=False, skip_ai=False):
        """
        Speed-optimized pipeline using Multi-threading for parallel processing.
        """
        from concurrent.futures import ThreadPoolExecutor
        
        results = [None] * len(image_paths)
        
        def process_single_image(idx, path):
            if not skip_ai:
                cleaned_filename = f"uploaded_cleaned_{idx}.jpg"
                cleaned_path = os.path.join(self.static_dir, cleaned_filename)
                success = self.ai_studio.remove_background(path, cleaned_path)
                results[idx] = "static/" + (cleaned_filename if success else os.path.basename(path))
            else:
                import shutil
                orig_filename = f"uploaded_orig_{idx}.jpg"
                shutil.copy(path, os.path.join(self.static_dir, orig_filename))
                results[idx] = "static/" + orig_filename

        # Process up to 6 images simultaneously
        with ThreadPoolExecutor(max_workers=6) as executor:
            for i, path in enumerate(image_paths):
                executor.submit(process_single_image, i, path)

        # AI Vision Analysis on the first image
        ai_metadata = self.ai_studio.analyze_product_with_ai(image_paths[0])
        
        result_data = {
            **ai_metadata,
            "original_price": "29.99",
            "image_paths": results,
            "source": "Turbo Multi-Upload"
        }
        return result_data

    def run_bulk_pipeline(self, urls, user_id, task_id):
        """
        더망고 스타일: 대량 상품 수집 및 가공 (백그라운드 처리용)
        """
        for idx, url in enumerate(urls):
            try:
                # 1. 개별 상품 수집 및 가공
                result = self.run_full_pipeline(url, skip_ai=False, user_id=user_id)
                
                # 2. DB 저장
                self.db.save_product(user_id, {
                    'url': url,
                    'title': result['title'],
                    'price': result['original_price'],
                    'category': result['category'],
                    'image_paths': [result['image_path']]
                })
                
                # 3. 진행률 업데이트
                self.db.update_task_progress(task_id, idx + 1)
                
            except Exception as e:
                print(f"Bulk Error at {url}: {e}")
        
        # 전체 작업 완료 처리
        self.db.complete_task(task_id)
        return True
