from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import numpy as np
import base64
import io
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_to_base64(img: Image.Image, fmt='PNG') -> str:
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def analyze_image(img: Image.Image):
    img_array = np.array(img)

    original_mode = img.mode

    if original_mode == 'L':
        is_grayscale = True
        gray_array = img_array
        r_channel = img_array
        g_channel = img_array
        b_channel = img_array

    elif original_mode in ('RGB', 'RGBA'):
        if original_mode == 'RGBA':
            img = img.convert('RGB')
            img_array = np.array(img)

        r_channel = img_array[:, :, 0]
        g_channel = img_array[:, :, 1]
        b_channel = img_array[:, :, 2]

        diff_rg = np.mean(np.abs(r_channel.astype(int) - g_channel.astype(int)))
        diff_rb = np.mean(np.abs(r_channel.astype(int) - b_channel.astype(int)))
        diff_gb = np.mean(np.abs(g_channel.astype(int) - b_channel.astype(int)))

        avg_diff = (diff_rg + diff_rb + diff_gb) / 3
        is_grayscale = avg_diff < 1.5 

        gray_array = (0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel).astype(np.uint8)
    else:
        img = img.convert('RGB')
        img_array = np.array(img)
        r_channel = img_array[:, :, 0]
        g_channel = img_array[:, :, 1]
        b_channel = img_array[:, :, 2]
        is_grayscale = False
        gray_array = (0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel).astype(np.uint8)

    height, width = img_array.shape[:2]

    def channel_stats(ch):
        return {
            'min': int(ch.min()),
            'max': int(ch.max()),
            'mean': round(float(ch.mean()), 2),
            'std': round(float(ch.std()), 2),
        }

    sample_size = 8
    h_s = min(sample_size, height)
    w_s = min(sample_size, width)

    def matrix_sample(ch):
        return ch[:h_s, :w_s].tolist()

    max_full = 64 
    h_f = min(max_full, height)
    w_f = min(max_full, width)

    def matrix_full(ch):
        return ch[:h_f, :w_f].tolist()

    gray_img = Image.fromarray(gray_array, mode='L')

    zeros = np.zeros_like(r_channel)

    r_visual = Image.fromarray(np.stack([r_channel, zeros, zeros], axis=2), 'RGB')
    g_visual = Image.fromarray(np.stack([zeros, g_channel, zeros], axis=2), 'RGB')
    b_visual = Image.fromarray(np.stack([zeros, zeros, b_channel], axis=2), 'RGB')

    result = {
        'is_grayscale': is_grayscale,
        'original_mode': original_mode,
        'width': width,
        'height': height,
        'channels': {
            'R': {
                'stats': channel_stats(r_channel),
                'sample': matrix_sample(r_channel),
                'full': matrix_full(r_channel),
                'visual_b64': image_to_base64(r_visual),
            },
            'G': {
                'stats': channel_stats(g_channel),
                'sample': matrix_sample(g_channel),
                'full': matrix_full(g_channel),
                'visual_b64': image_to_base64(g_visual),
            },
            'B': {
                'stats': channel_stats(b_channel),
                'sample': matrix_sample(b_channel),
                'full': matrix_full(b_channel),
                'visual_b64': image_to_base64(b_visual),
            },
        },
        'grayscale': {
            'stats': channel_stats(gray_array),
            'full': matrix_full(gray_array),
            'image_b64': image_to_base64(gray_img),
            'formula': 'Y = 0.299·R + 0.587·G + 0.114·B',
        },
        'sample_size': {'h': h_s, 'w': w_s},
        'full_size': {'h': h_f, 'w': w_f},
    }

    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'Tidak ada file gambar yang dikirim.'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nama file kosong.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Format file tidak didukung. Gunakan PNG, JPG, BMP, atau WEBP.'}), 400

    try:
        img = Image.open(file.stream)
        orig_b64 = image_to_base64(img.convert('RGB'))
        result = analyze_image(img)
        result['original_b64'] = orig_b64
        result['filename'] = file.filename
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Gagal memproses gambar: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)