from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import sys
import time
from functools import wraps

# Add parent directory to path to import pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import AutomationPipeline

app = Flask(__name__)
app.secret_key = "dobi_premium_saas_key" # 상용 서비스 시 암호화 키로 변경 필요
pipeline = AutomationPipeline()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({"status": "error", "message": "Login required"}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email')
    if pipeline.db.create_user(email):
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "이미 존재하는 이메일이거나 오류가 발생했습니다."}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    # DB에서 사용자 확인
    user = pipeline.db._get_connection().execute("SELECT * FROM Users WHERE email = ?", (email,)).fetchone()
    if user:
        session['user_id'] = user['user_id']
        session['email'] = user['email']
        pipeline.db.log_activity(user['user_id'], "LOGIN", "User logged in via Web")
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "등록되지 않은 사용자입니다."}), 404

@app.route('/api/logout')
def api_logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/api/process', methods=['POST'])
@login_required
def api_process():
    """URL 단일 수집 API"""
    data = request.json
    url = data.get('url')
    skip_ai = data.get('skip_ai', False)
    user_id = session['user_id']
    
    try:
        pipeline.db.log_activity(user_id, "SCRAPE_START", f"URL: {url}")
        result = pipeline.run_full_pipeline(url, skip_ai=skip_ai, user_id=user_id)
        
        product_id = pipeline.db.save_product(user_id, {
            'url': url,
            'title': result['title'],
            'price': result['original_price'],
            'category': result['category'],
            'image_paths': [result['image_path']]
        })
        
        result['product_id'] = product_id
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bulk_source', methods=['POST'])
@login_required
def api_bulk_source():
    """더망고 스타일: 대량 수집 시작 (비동기)"""
    data = request.json
    urls = data.get('urls', [])
    user_id = session['user_id']
    
    if not urls:
        return jsonify({"status": "error", "message": "수집할 URL이 없습니다."}), 400

    task_id = pipeline.db.create_task(user_id, 'bulk_source', len(urls))
    
    import threading
    thread = threading.Thread(target=pipeline.run_bulk_pipeline, args=(urls, user_id, task_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "success", "task_id": task_id})

@app.route('/api/task_status/<int:task_id>')
@login_required
def api_task_status(task_id):
    """작업 진행 현황 확인 API"""
    with pipeline.db._get_connection() as conn:
        task = conn.execute("SELECT * FROM SourcingTasks WHERE task_id = ?", (task_id,)).fetchone()
    
    if task:
        return jsonify({
            "status": task['status'],
            "total": task['total_count'],
            "current": task['current_count'],
            "percent": round((task['current_count'] / task['total_count'] * 100) if task['total_count'] > 0 else 0, 1)
        })
    return jsonify({"status": "error", "message": "작업을 찾을 수 없습니다."}), 404

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Mobile-first API for direct photo uploads from phone camera"""
    if 'files' not in request.files:
        return jsonify({"status": "error", "message": "No files provided"}), 400
    
    files = request.files.getlist('files')
    skip_ai = request.form.get('skip_ai') == 'true'
    user_id = request.form.get('user_id', 1)
    
    try:
        upload_paths = []
        for i, file in enumerate(files[:6]):
            filename = f"user_{user_id}_upload_{int(time.time())}_{i}.jpg"
            upload_path = os.path.join(pipeline.static_dir, filename)
            file.save(upload_path)
            upload_paths.append(upload_path)
        
        result = pipeline.run_image_pipeline(upload_paths, skip_ai=skip_ai)
        
        # Save draft to DB
        product_id = pipeline.db.save_product(user_id, {
            'url': 'Direct Upload',
            'title': result['title'],
            'price': result['original_price'],
            'category': result['category'],
            'image_paths': result['image_paths']
        })
        
        result['product_id'] = product_id
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/list', methods=['POST'])
def api_list():
    """Final eBay listing execution API for App/Web"""
    data = request.json
    product_id = data.get('product_id')
    manual_price = data.get('price')
    manual_title = data.get('title')
    
    try:
        sku = f"KGOODS_{int(time.time())}"
        item_data = {
            "title": manual_title or "K-Goods Item",
            "description": "Professional Listed via DOBI SaaS",
            "image_url": "https://i.ebayimg.com/images/g/example/s-l500.jpg" # API Placeholder
        }
        
        if pipeline.listing_manager.create_or_replace_inventory_item(sku, item_data):
            offer_id = pipeline.listing_manager.create_offer(sku, manual_price or 25.0)
            if offer_id:
                listing_id = pipeline.listing_manager.publish_offer(offer_id)
                
                # Update Database status
                if product_id:
                    pipeline.db.update_ebay_listing(product_id, listing_id)
                
                return jsonify({"status": "success", "listing_id": listing_id})
        
        return jsonify({"status": "error", "message": "Ebay listing failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_thumb', methods=['POST'])
def generate_thumb():
    data = request.json
    path = data.get('path')
    prompt = data.get('prompt')
    
    try:
        # [AI Thumbnail Logic] 
        # In a real SaaS, you would call DALL-E or Stability AI here.
        # For now, we simulate by creating a 'Creative Background' version.
        new_filename = f"thumb_{int(time.time())}.jpg"
        new_path = os.path.join(pipeline.static_dir, new_filename)
        
        # Mocking: In actual implementation, replace with Generative AI API
        # For demonstration, we'll use a high-quality refine as a placeholder
        pipeline.ai_studio.remove_background(os.path.join(os.path.dirname(os.path.abspath(__file__)), path), new_path, precision=True)
        
        print(f"🎨 AI Thumbnail requested with prompt: {prompt}")
        return jsonify({"new_path": f"static/{new_filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin')
def admin_dashboard():
    """관리자 전용 통계 페이지"""
    return render_template('admin.html')

@app.route('/api/admin/stats')
def api_admin_stats():
    """SaaS 운영 지표 데이터 제공"""
    try:
        # 1. 기본 통계
        with pipeline.db._get_connection() as conn:
            user_count = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
            product_count = conn.execute("SELECT COUNT(*) FROM Products").fetchone()[0]
            recent_logs = conn.execute("SELECT * FROM ActivityLogs ORDER BY timestamp DESC LIMIT 10").fetchall()
        
        # 2. 분석 데이터 (카테고리, 소싱처)
        analytics = pipeline.db.get_analytics()
        
        return jsonify({
            "status": "success",
            "total_users": user_count,
            "total_listings": product_count,
            "analytics": analytics,
            "recent_logs": [dict(l) for l in recent_logs]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
def upload_file():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    files = request.files.getlist('files')
    skip_ai = request.form.get('skip_ai') == 'true'
    
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    upload_paths = []
    for i, file in enumerate(files[:6]):
        upload_path = os.path.join(pipeline.static_dir, f"temp_upload_{i}.jpg")
        file.save(upload_path)
        upload_paths.append(upload_path)
    
    try:
        result = pipeline.run_image_pipeline(upload_paths, skip_ai=skip_ai)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
