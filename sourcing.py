import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random

class SourcingEngine:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

    def scrape_product(self, url):
        # Human-like delay to avoid detection
        time.sleep(random.uniform(1, 3))
        
        if "musinsa.com" in url:
            return self._scrape_musinsa(url)
        return None

    def _scrape_musinsa(self, url):
        print(f"Scraping Musinsa: {url}")
        try:
            session = requests.Session()
            response = session.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Access denied: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Title
            title = ""
            title_meta = soup.find("meta", property="og:title")
            if title_meta:
                title = title_meta["content"].split("|")[0].strip()
            
            # Images
            image_urls = []
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_urls.append(og_image["content"])
            
            # Find all high-quality images in detail section
            for img in soup.find_all("img"):
                src = img.get('src') or img.get('data-src')
                if src and "goods_img" in src: # Filter for product goods images
                    if not src.startswith('http'): src = "https:" + src
                    image_urls.append(src)

            # Price
            price = "0"
            price_meta = soup.find("meta", property="product:price:amount")
            if price_meta:
                price = price_meta["content"]
            else:
                desc_meta = soup.find("meta", property="og:description")
                if desc_meta:
                    match = re.search(r'([\d,]+)원?', desc_meta["content"])
                    if match: price = match.group(1).replace(",", "")

            return {
                "source": "Musinsa",
                "title": title,
                "price": price,
                "image_urls": list(set(image_urls)),
                "category": "Beauty",
                "original_url": url
            }
        except Exception as e:
            print(f"Error scraping Musinsa: {e}")
            return None
