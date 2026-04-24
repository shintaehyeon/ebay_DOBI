import os
from PIL import Image
import io
from rembg import remove, new_session

class AIStudio:
    def __init__(self, remove_bg_key=None, ai_vision_key=None):
        self.remove_bg_key = remove_bg_key
        self.ai_vision_key = ai_vision_key
        # Switch to 'isnet-general-use' for high-precision edge detection
        self.session = new_session("isnet-general-use") 

    def pick_best_image(self, image_urls):
        return image_urls[0] if image_urls else None

    def remove_background(self, image_path, output_path):
        """
        High-precision background removal with ISNet model.
        Includes Alpha Matting to fix blurry edges on dark objects.
        """
        print(f"High-precision cleaning: {image_path}...")
        try:
            with open(image_path, 'rb') as i:
                input_image = i.read()
                
                # Use alpha_matting for sharper edges on complex items like pumps
                output_data = remove(
                    input_image, 
                    session=self.session,
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=240,
                    alpha_matting_background_threshold=10,
                    alpha_matting_erode_size=10
                )
                
                img = Image.open(io.BytesIO(output_data)).convert("RGBA")
                white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                final_img = Image.alpha_composite(white_bg, img)
                
                final_img.convert("RGB").save(output_path, "JPEG", quality=100)
            
            print(f"Professional clean image saved: {output_path}")
            return True
        except Exception as e:
            print(f"Error in precision removal: {e}")
            return False

    def analyze_product_with_ai(self, image_path):
        # AI metadata generation placeholder
        return {
            "title": "AI Optimized Luxury Beauty Product",
            "category": "Beauty > Body Care",
            "description": "Premium formula for glowing skin...",
            "condition": "New"
        }
