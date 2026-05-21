import os
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

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
        try:
            in_memory_file = file.read()
            nparr = np.frombuffer(in_memory_file, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                return jsonify({'error': 'Invalid or corrupted image file'}), 400
                
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
            
            h, w, c = img_rgb.shape
            total_pixels = h * w
            

            s_channel = img_hsv[:, :, 1]
            mean_saturation = float(np.mean(s_channel))
            colored_pixel_ratio = float(np.sum(s_channel > 15) / total_pixels * 100)
            
            if mean_saturation < 8 or colored_pixel_ratio < 1.0:
                img_type = "Grayscale Image"
                reason = f"Mean Saturation ({mean_saturation:.2f}) < 8 or Colored Ratio ({colored_pixel_ratio:.2f}%) < 1%"
            else:
                img_type = "Colored Image"
                reason = f"Mean Saturation ({mean_saturation:.2f}) >= 8 and Colored Ratio ({colored_pixel_ratio:.2f}%) >= 1%"
                

            import base64
            encoded_img = base64.b64encode(in_memory_file).decode('utf-8')
            mime_type = file.mimetype if file.mimetype else 'image/jpeg'
            image_url = f"data:{mime_type};base64,{encoded_img}"
            

            r_img_bgr = np.zeros_like(img_bgr)
            r_img_bgr[:,:,2] = img_rgb[:,:,0]
            _, buffer_r = cv2.imencode('.jpg', r_img_bgr)
            url_r = f"data:image/jpeg;base64,{base64.b64encode(buffer_r).decode('utf-8')}"
            
            g_img_bgr = np.zeros_like(img_bgr)
            g_img_bgr[:,:,1] = img_rgb[:,:,1]
            _, buffer_g = cv2.imencode('.jpg', g_img_bgr)
            url_g = f"data:image/jpeg;base64,{base64.b64encode(buffer_g).decode('utf-8')}"
            
            b_img_bgr = np.zeros_like(img_bgr)
            b_img_bgr[:,:,0] = img_rgb[:,:,2]
            _, buffer_b = cv2.imencode('.jpg', b_img_bgr)
            url_b = f"data:image/jpeg;base64,{base64.b64encode(buffer_b).decode('utf-8')}"
            

            def get_stats(channel_data):
                return {
                    'min': int(np.min(channel_data)),
                    'max': int(np.max(channel_data)),
                    'mean': round(float(np.mean(channel_data)), 2),
                    'std': round(float(np.std(channel_data)), 2)
                }
            
            stats = {
                'r': get_stats(img_rgb[:,:,0]),
                'g': get_stats(img_rgb[:,:,1]),
                'b': get_stats(img_rgb[:,:,2])
            }
            

            mat_h = min(16, h)
            mat_w = min(16, w)
            matrix_data = {
                'r': img_rgb[0:mat_h, 0:mat_w, 0].tolist(),
                'g': img_rgb[0:mat_h, 0:mat_w, 1].tolist(),
                'b': img_rgb[0:mat_h, 0:mat_w, 2].tolist()
            }
            

            hist_r = cv2.calcHist([img_rgb], [0], None, [256], [0, 256]).flatten().tolist()
            hist_g = cv2.calcHist([img_rgb], [1], None, [256], [0, 256]).flatten().tolist()
            hist_b = cv2.calcHist([img_rgb], [2], None, [256], [0, 256]).flatten().tolist()
            
            return jsonify({
                'success': True,
                'image_url': image_url,
                'type': img_type,
                'reason': reason,
                'hsv_metrics': {
                    'mean_saturation': round(mean_saturation, 2),
                    'colored_ratio': round(colored_pixel_ratio, 2)
                },
                'resolution': f"{w}x{h}",
                'total_pixels': total_pixels,
                'histogram': {
                    'r': hist_r,
                    'g': hist_g,
                    'b': hist_b
                },
                'channels': {
                    'r': url_r,
                    'g': url_g,
                    'b': url_b
                },
                'stats': stats,
                'matrix': matrix_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({'error': 'Unsupported file format. Please upload JPG, JPEG, or PNG.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)