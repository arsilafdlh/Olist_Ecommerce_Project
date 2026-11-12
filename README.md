# Olist E-Commerce Analytics Project

## Deskripsi Proyek

Proyek ini merupakan analisis data terhadap Olist Brazilian E-Commerce Public Dataset. Analisis dilakukan untuk memahami performa transaksi penjualan, kontribusi kategori produk, karakteristik pelanggan, serta hubungan antara ketepatan waktu pengiriman dan ulasan pelanggan.

Hasil analisis disajikan dalam bentuk notebook Google Colab dan dashboard interaktif menggunakan Streamlit.

## Tujuan Analisis

1. Menganalisis tren nilai transaksi dan volume pesanan berdasarkan periode waktu.
2. Mengidentifikasi kategori produk dengan kontribusi transaksi tertinggi.
3. Mengelompokkan pelanggan berdasarkan karakteristik transaksi menggunakan RFM dan segmentasi nilai pelanggan.
4. Menganalisis hubungan ketepatan waktu pengiriman dengan skor ulasan pelanggan.
5. Melihat distribusi pelanggan dan aktivitas transaksi berdasarkan wilayah geografis.

## Dataset

Dataset yang digunakan adalah Olist Brazilian E-Commerce Public Dataset.

Dataset terdiri dari beberapa tabel, antara lain:
- Customers
- Orders
- Order Items
- Order Payments
- Order Reviews
- Products
- Sellers
- Geolocation
- Product Category Translation

Dataset telah melalui tahapan data gathering, assessing, cleaning, dan exploratory data analysis (EDA).

## Metode Analisis

Analisis yang dilakukan meliputi:

- Data Wrangling: pengumpulan, pemeriksaan, dan pembersihan data.
- Exploratory Data Analysis (EDA): eksplorasi pola transaksi, kategori produk, pelanggan, dan pengiriman.
- RFM Analysis: segmentasi pelanggan berdasarkan Recency, Frequency, dan Monetary.
- Customer Value Segmentation: pengelompokan pelanggan berdasarkan nilai transaksi.
- Geographical Analysis: analisis distribusi pelanggan berdasarkan wilayah.
- Data Visualization: penyajian hasil analisis dalam bentuk grafik dan dashboard interaktif.

## Dashboard

Dashboard dikembangkan menggunakan Streamlit dan memiliki beberapa halaman:

1. Overview: ringkasan indikator utama performa e-commerce.
2. Sales Performance: tren nilai transaksi dan jumlah pesanan.
3. Product Categories: analisis kontribusi kategori produk.
4. Customer Segmentation: segmentasi pelanggan.
5. Delivery & Reviews: analisis pengiriman dan ulasan pelanggan.
6. Geographical Analysis: persebaran pelanggan berdasarkan wilayah.

## Struktur Folder

```text
Olist_Ecommerce_Project/
│
├── data/
│   ├── sales_data.csv
│   ├── monthly_sales.csv
│   ├── category_sales.csv
│   ├── rfm_data.csv
│   ├── segment_summary.csv
│   ├── customer_value_summary.csv
│   ├── delivery_summary.csv
│   ├── state_customer_summary.csv
│   └── state_geo_summary.csv
│
├── dashboard.py
├── requirements.txt
├── README.md
└── url.txt
```

## Instalasi dan Cara Menjalankan Dashboard

### 1. Persiapan

Pastikan Python sudah terpasang di komputer.

### 2. Install Library

Buka terminal pada folder proyek, kemudian jalankan:

```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard

Jalankan perintah berikut:

```bash
streamlit run dashboard.py
```

### 4. Akses Dashboard

Setelah berhasil dijalankan, buka alamat berikut melalui browser:

```text
http://localhost:8501
```

Pastikan folder `data` beserta seluruh file CSV hasil pengolahan berada di dalam folder proyek.

## Teknologi yang Digunakan

- Python
- Pandas
- Streamlit
- Plotly
- Matplotlib
- Seaborn
- Google Colab
