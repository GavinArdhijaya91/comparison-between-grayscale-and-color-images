import io
import base64
import random
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from flask import Flask, render_template, request, jsonify
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64

def img_to_b64(img_array, fmt='PNG'):
    pil_img = Image.fromarray(img_array)
    buf = io.BytesIO()
    pil_img.save(buf, format=fmt)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def get_stats(arr):
    return {
        'min': int(np.min(arr)),
        'max': int(np.max(arr)),
        'mean': round(float(np.mean(arr)), 2),
        'std': round(float(np.std(arr)), 2),
    }

def make_channel_histogram(channel_data, color, label):
    fig, ax = plt.subplots(figsize=(3.5, 2.2), dpi=110)
    fig.patch.set_facecolor('#13161e')
    ax.set_facecolor('#1a1e2a')
    hist, bins = np.histogram(channel_data.flatten(), bins=64, range=(0, 255))
    ax.fill_between(range(len(hist)), hist, color=color, alpha=0.75)
    ax.plot(range(len(hist)), hist, color=color, linewidth=1.2)
    ax.set_xlim(0, 63)
    ax.set_xlabel('Intensity', color='#7a8399', fontsize=7)
    ax.set_ylabel('Count', color='#7a8399', fontsize=7)
    ax.tick_params(colors='#7a8399', labelsize=6)
    for spine in ax.spines.values():
        spine.set_edgecolor('#252a38')
    ax.grid(axis='y', color='#252a38', linewidth=0.5, alpha=0.7)
    fig.tight_layout(pad=0.5)
    return fig_to_b64(fig)

def make_histogram_rgb(r, g, b):
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=110)
    fig.patch.set_facecolor('#13161e')
    ax.set_facecolor('#1a1e2a')
    for data, color, label in [(r, '#ff5f6d', 'Red'), (g, '#4ecb8d', 'Green'), (b, '#5b8dee', 'Blue')]:
        hist, _ = np.histogram(data.flatten(), bins=128, range=(0, 255))
        ax.plot(range(len(hist)), hist, color=color, linewidth=1.5, label=label, alpha=0.9)
        ax.fill_between(range(len(hist)), hist, color=color, alpha=0.15)
    ax.set_xlim(0, 127)
    ax.set_xlabel('Pixel Intensity (0–255)', color='#7a8399', fontsize=8)
    ax.set_ylabel('Pixel Count', color='#7a8399', fontsize=8)
    ax.tick_params(colors='#7a8399', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#252a38')
    ax.grid(color='#252a38', linewidth=0.5, alpha=0.6)
    ax.legend(facecolor='#1a1e2a', edgecolor='#252a38', labelcolor='#e8ecf4', fontsize=8)
    fig.tight_layout(pad=0.6)
    return fig_to_b64(fig)

def make_bar_stats(r, g, b):
    channels = ['Red', 'Green', 'Blue']
    colors = ['#ff5f6d', '#4ecb8d', '#5b8dee']
    means = [np.mean(r), np.mean(g), np.mean(b)]
    stds = [np.std(r), np.std(g), np.std(b)]
    x = np.arange(3)
    width = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=110)
    fig.patch.set_facecolor('#13161e')
    ax.set_facecolor('#1a1e2a')
    bars1 = ax.bar(x - width/2, means, width, label='Mean', color=colors, alpha=0.85)
    bars2 = ax.bar(x + width/2, stds, width, label='Std Dev', color=colors, alpha=0.45, hatch='//')
    ax.set_xticks(x)
    ax.set_xticklabels(channels, color='#e8ecf4', fontsize=9)
    ax.set_ylabel('Pixel Value', color='#7a8399', fontsize=8)
    ax.tick_params(colors='#7a8399', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#252a38')
    ax.grid(axis='y', color='#252a38', linewidth=0.5, alpha=0.6)
    ax.legend(facecolor='#1a1e2a', edgecolor='#252a38', labelcolor='#e8ecf4', fontsize=8)
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{bar.get_height():.1f}', ha='center', va='bottom', color='#e8ecf4', fontsize=6.5)
    fig.tight_layout(pad=0.6)
    return fig_to_b64(fig)

def make_heatmap_saturation(hsv_img, max_size=256):
    s_channel = hsv_img[:, :, 1].astype(float)
    h, w = s_channel.shape
    if h > max_size or w > max_size:
        scale = max_size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        s_channel = cv2.resize(s_channel, (new_w, new_h), interpolation=cv2.INTER_AREA)
    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=110)
    fig.patch.set_facecolor('#13161e')
    ax.set_facecolor('#1a1e2a')
    im = ax.imshow(s_channel, cmap='YlOrRd', aspect='auto', vmin=0, vmax=255)
    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.ax.tick_params(colors='#7a8399', labelsize=7)
    cbar.set_label('Saturation Value', color='#7a8399', fontsize=8)
    ax.set_xlabel('Width (px)', color='#7a8399', fontsize=8)
    ax.set_ylabel('Height (px)', color='#7a8399', fontsize=8)
    ax.tick_params(colors='#7a8399', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#252a38')
    fig.tight_layout(pad=0.6)
    return fig_to_b64(fig)

def make_scatter_rgb(r, g, b, n_samples=500):
    total = r.size
    indices = np.random.choice(total, min(n_samples, total), replace=False)
    rs = r.flatten()[indices].astype(int)
    gs = g.flatten()[indices].astype(int)
    bs = b.flatten()[indices].astype(int)
    colors_rgb = np.stack([rs, gs, bs], axis=1) / 255.0
    sizes = (bs / 10) + 10
    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=110)
    fig.patch.set_facecolor('#13161e')
    ax.set_facecolor('#1a1e2a')
    ax.scatter(rs, gs, c=colors_rgb, s=sizes, alpha=0.7, edgecolors='none')
    ax.set_xlabel('Red Channel Value', color='#7a8399', fontsize=8)
    ax.set_ylabel('Green Channel Value', color='#7a8399', fontsize=8)
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.tick_params(colors='#7a8399', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#252a38')
    ax.grid(color='#252a38', linewidth=0.5, alpha=0.5)
    ax.text(0.98, 0.02, 'dot size ∝ Blue', transform=ax.transAxes,
            ha='right', va='bottom', color='#7a8399', fontsize=7)
    fig.tight_layout(pad=0.6)
    return fig_to_b64(fig)

def make_grayscale_comparison_chart(r, g, b, gray):
    labels = ['Red', 'Green', 'Blue', 'Grayscale (Y)']
    means = [np.mean(r), np.mean(g), np.mean(b), np.mean(gray)]
    colors = ['#ff5f6d', '#4ecb8d', '#5b8dee', '#a0a8c0']
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=110)
    fig.patch.set_facecolor('#13161e')
    ax.set_facecolor('#1a1e2a')
    bars = ax.bar(labels, means, color=colors, alpha=0.85)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{bar.get_height():.1f}', ha='center', va='bottom', color='#e8ecf4', fontsize=8)
    ax.set_ylabel('Mean Value', color='#7a8399', fontsize=8)
    ax.set_ylim(0, 275)
    ax.tick_params(colors='#e8ecf4', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#252a38')
    ax.grid(axis='y', color='#252a38', linewidth=0.5, alpha=0.6)
    fig.tight_layout(pad=0.6)
    return fig_to_b64(fig)

def build_matrix_subset(channel_data, max_dim=64):
    h, w = channel_data.shape
    sub = channel_data[:min(max_dim, h), :min(max_dim, w)]
    return sub.tolist(), sub.shape

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    if not file or file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file. Use PNG, JPG, BMP, or WEBP'}), 400

    try:
        raw = file.read()
        pil_img = Image.open(io.BytesIO(raw))
        original_mode = pil_img.mode

        if original_mode in ('L', 'LA', 'P'):
            pil_rgb = pil_img.convert('RGB')
            direct_grayscale = True
        else:
            pil_rgb = pil_img.convert('RGB')
            direct_grayscale = False

        img_rgb = np.array(pil_rgb)
        height, width = img_rgb.shape[:2]
        total_pixels = height * width

        r = img_rgb[:, :, 0]
        g = img_rgb[:, :, 1]
        b = img_rgb[:, :, 2]

        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        mean_saturation = float(np.mean(img_hsv[:, :, 1]))
        colored_px_ratio = float(np.sum(img_hsv[:, :, 1] > 15) / total_pixels)

        if direct_grayscale or mean_saturation < 8 or colored_px_ratio < 0.01:
            is_grayscale = True
        else:
            is_grayscale = False

        original_b64 = base64.b64encode(raw).decode('utf-8')
        mime = file.mimetype or 'image/jpeg'

        gray_arr = np.array(pil_rgb.convert('L'))
        gray_rgb_arr = np.stack([gray_arr] * 3, axis=-1)
        gray_b64 = img_to_b64(gray_rgb_arr)
        gray_stats = get_stats(gray_arr)
        gray_matrix, gray_matrix_shape = build_matrix_subset(gray_arr)

        r_img = np.zeros_like(img_rgb); r_img[:, :, 0] = r
        g_img = np.zeros_like(img_rgb); g_img[:, :, 1] = g
        b_img = np.zeros_like(img_rgb); b_img[:, :, 2] = b

        r_matrix, r_matrix_shape = build_matrix_subset(r)
        g_matrix, g_matrix_shape = build_matrix_subset(g)
        b_matrix, b_matrix_shape = build_matrix_subset(b)

        channels = {
            'R': {
                'image_b64': img_to_b64(r_img),
                'stats': get_stats(r),
                'histogram_b64': make_channel_histogram(r, '#ff5f6d', 'Red'),
                'matrix': r_matrix,
                'matrix_shape': list(r_matrix_shape),
            },
            'G': {
                'image_b64': img_to_b64(g_img),
                'stats': get_stats(g),
                'histogram_b64': make_channel_histogram(g, '#4ecb8d', 'Green'),
                'matrix': g_matrix,
                'matrix_shape': list(g_matrix_shape),
            },
            'B': {
                'image_b64': img_to_b64(b_img),
                'stats': get_stats(b),
                'histogram_b64': make_channel_histogram(b, '#5b8dee', 'Blue'),
                'matrix': b_matrix,
                'matrix_shape': list(b_matrix_shape),
            },
        }

        charts = {
            'histogram_rgb_b64': make_histogram_rgb(r, g, b),
            'bar_stats_b64': make_bar_stats(r, g, b),
            'heatmap_saturation_b64': make_heatmap_saturation(img_hsv),
            'scatter_rgb_b64': make_scatter_rgb(r, g, b),
        }

        grayscale_section = {
            'image_b64': gray_b64,
            'stats': gray_stats,
            'matrix': gray_matrix,
            'matrix_shape': list(gray_matrix_shape),
            'comparison_chart_b64': make_grayscale_comparison_chart(r, g, b, gray_arr),
        }

        return jsonify({
            'success': True,
            'is_grayscale': is_grayscale,
            'original_mode': original_mode,
            'width': width,
            'height': height,
            'total_pixels': total_pixels,
            'mean_saturation': round(mean_saturation, 4),
            'colored_pixel_ratio': round(colored_px_ratio, 4),
            'original_b64': original_b64,
            'original_mime': mime,
            'channels': channels,
            'charts': charts,
            'grayscale': grayscale_section,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)