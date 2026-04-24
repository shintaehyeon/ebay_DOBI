from flask import Flask, render_template, request, jsonify
import os
import sys

# Add parent directory to path to import pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import ListingPipeline

app = Flask(__name__)

# Initialize pipeline with keys (Replace with actual keys or use .env)
EBAY_TOKEN = os.getenv("EBAY_TOKEN", "YOUR_EBAY_TOKEN")
REMOVE_BG_KEY = os.getenv("REMOVE_BG_KEY", "YOUR_REMOVE_BG_KEY")

pipeline = ListingPipeline(ebay_token=EBAY_TOKEN, remove_bg_key=REMOVE_BG_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    # Run the pipeline
    try:
        result = pipeline.process_url_to_ebay(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
