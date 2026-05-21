import os
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Save file with unique name
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Process image
            # OpenCV reads in BGR format
            img_bgr = cv2.imread(filepath)
            if img_bgr is None:
                return jsonify({'error': 'Invalid or corrupted image file'}), 400
                
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            # Dimensions
            h, w, c = img_rgb.shape
            total_pixels = h * w
            
            # Grayscale Analysis
            # Calculate standard deviation across RGB channels for each pixel
            # A pixel with R=G=B will have std dev = 0
            std_dev = np.std(img_rgb, axis=2)
            mean_std_dev = np.mean(std_dev)
            
            # Max possible standard deviation is for [255, 0, 0] which is ~120.2
            max_possible_std_dev = np.std([255, 0, 0])
            similarity = max(0, 100 - (mean_std_dev / max_possible_std_dev * 100))
            
            # Determine type
            threshold = 95.0
            if similarity >= threshold:
                img_type = "Grayscale Image"
            else:
                img_type = "Colored Image"
                
            # Generate Histograms
            hist_r = cv2.calcHist([img_rgb], [0], None, [256], [0, 256]).flatten().tolist()
            hist_g = cv2.calcHist([img_rgb], [1], None, [256], [0, 256]).flatten().tolist()
            hist_b = cv2.calcHist([img_rgb], [2], None, [256], [0, 256]).flatten().tolist()
            
            image_url = url_for('static', filename=f'uploads/{unique_filename}')
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'type': img_type,
                'similarity': round(similarity, 2),
                'resolution': f"{w}x{h}",
                'total_pixels': total_pixels,
                'histogram': {
                    'r': hist_r,
                    'g': hist_g,
                    'b': hist_b
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Unsupported file format. Please upload JPG, JPEG, or PNG.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)