# Comparison Between Grayscale and Color Images

[![Live Preview on Vercel](https://img.shields.io/badge/Live_Preview-Vercel-black?style=for-the-badge&logo=vercel)](https://comparison-between-grayscale-and-co.vercel.app/)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/GavinArdhijaya91/comparison-between-grayscale-and-color-images)

## 📖 Deskripsi
Aplikasi web interaktif berbasis Python yang digunakan untuk mengidentifikasi dan membandingkan gambar berwarna (RGB) dengan gambar skala abu-abu (Grayscale). Aplikasi ini dibangun dengan menerapkan konsep-konsep dasar **Aljabar Linear** (Linear Algebra) dan pengolahan citra digital untuk melakukan analisis matematis pada piksel gambar.

## 🔬 Latar Belakang
Setiap gambar digital pada dasarnya adalah representasi dari kumpulan angka yang disusun dalam bentuk **Matriks**. 
- Gambar **Grayscale** adalah matriks 2 Dimensi dimana setiap elemen berisi nilai intensitas cahaya (0-255).
- Gambar **RGB (Berwarna)** adalah matriks 3 Dimensi (Tensor) yang terdiri dari kombinasi vektor channel Merah (Red), Hijau (Green), dan Biru (Blue).

Proyek ini dibangun untuk mendemonstrasikan secara visual dan matematis bagaimana operasi matriks dan vektor berperan penting dalam dunia komputasi visual.

## 🎯 Tujuan
1. Menerima input gambar dari pengguna (maksimal 10MB).
2. Membaca dan mengekstrak nilai piksel matriks dari gambar yang diunggah.
3. Mengklasifikasikan gambar menjadi `Colored Image` atau `Grayscale Image` berdasarkan perhitungan simpangan baku antar *channel* RGB.
4. Menampilkan visualisasi data matematis berupa **RGB Histogram**.
5. Menyediakan platform edukasi interaktif mengenai transformasi linear pada citra.

## ⚙️ Cara Kerja Sistem
1. **Ekstraksi Matriks**: Gambar yang diunggah dikonversi ke dalam bentuk array (matriks) NumPy.
2. **Analisis Vektor RGB**: Sistem menghitung simpangan baku (Standard Deviation) untuk komponen Red, Green, dan Blue pada setiap piksel.
3. **Persamaan Linear Grayscale**: Konversi standar grayscale menggunakan kombinasi linear berbobot:
   $$Y = 0.299R + 0.587G + 0.114B$$
4. **Klasifikasi**: Apabila jarak antara vektor warna sangat kecil (kondisi $R \approx G \approx B$), maka gambar akan diklasifikasikan sebagai *Grayscale*. Jika terdapat perbedaan signifikan (misalnya $R \neq G \neq B$), gambar akan diklasifikasikan sebagai *Colored Image*.
5. **Visualisasi Histogram**: Chart.js (di versi Flask) / Matplotlib (di versi Streamlit) akan membaca distribusi frekuensi intensitas warna (0-255) pada gambar dan membuat plot grafik garis.

---

## 🚀 Cara Clone & Menjalankan di Komputer Lokal

Proyek ini mendukung dua arsitektur berbeda: **Flask** (untuk UI Custom yang memukau) dan **Streamlit** (untuk kesederhanaan deployment). Keduanya memiliki fungsi backend yang identik.

### 1. Clone Repository
Buka Terminal / Command Prompt dan jalankan:
```bash
git clone https://github.com/GavinArdhijaya91/comparison-between-grayscale-and-color-images.git
cd comparison-between-grayscale-and-color-images
```

### 2. Install Dependencies
Sangat disarankan menggunakan Virtual Environment agar library tidak bentrok.
```bash
# Membuat virtual environment
python -m venv venv

# Mengaktifkan virtual environment (Windows)
.\venv\Scripts\activate
# Mengaktifkan virtual environment (Mac/Linux)
source venv/bin/activate

# Install semua library yang dibutuhkan
pip install -r requirements.txt
```

### 3. Menjalankan Aplikasi

Kamu bisa memilih salah satu dari dua cara di bawah ini:

#### Opsi A: Menjalankan Versi Flask (Rekomendasi untuk UI Keren)
```bash
python app.py
```
👉 Kemudian buka browser dan kunjungi: **http://127.0.0.1:5000**

#### Opsi B: Menjalankan Versi Streamlit
```bash
streamlit run streamlit_app.py
```
👉 Halaman aplikasi akan otomatis terbuka di browser.

---

## 🛠️ Tech Stack
* **Python 3.10+** (OpenCV, NumPy, Pillow)
* **Frontend Flask**: HTML5, Vanilla CSS3 (Glassmorphism UI), Vanilla JavaScript, Chart.js
* **Frontend Streamlit**: Streamlit Native Widgets, Matplotlib
* **Deployment**: Vercel (untuk Flask), Streamlit Community Cloud (untuk Streamlit)
