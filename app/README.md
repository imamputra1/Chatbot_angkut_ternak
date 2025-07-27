# Chatbot WhatsApp Pemesanan Angkut Ternak

Ini adalah proyek chatbot WhatsApp yang dibangun menggunakan Python dan FastAPI untuk mengotomatisasi proses pemesanan jasa angkut ternak.

## Fitur

- **Percakapan Berurutan**: Memandu pengguna langkah-demi-langkah dalam mengisi form pemesanan.
- **Dua Fungsi Utama**:
  1.  **Buat Pesanan Baru**: Mengumpulkan data nama, jenis hewan, lokasi jemput, lokasi tujuan, dan jadwal.
  2.  **Cek Status Pesanan**: Mengambil data pesanan terakhir berdasarkan nomor HP pelanggan.
- **Integrasi Google Sheets**: Menggunakan Google Sheets sebagai database sederhana untuk menyimpan dan membaca data pesanan.
- **Notifikasi Admin**: Mengirimkan notifikasi WhatsApp otomatis ke nomor admin setiap ada pesanan baru yang masuk.

## Teknologi yang Digunakan

- **Backend**: Python 3.10+
- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: Google Sheets (via `gspread`)
- **API Gateway**: WhatsApp Cloud API
- **Tunneling (Development)**: Ngrok

## Struktur Proyek

|-- app/
| |-- init.py
| |-- main.py # Logika utama FastAPI & Webhook
| |-- gsheets_client.py # Fungsi interaksi dengan Google Sheets
| |-- ...
|-- client_secret.json # Kredensial Google Cloud (JANGAN DI-PUSH KE GITHUB)
|-- .env # Variabel lingkungan & secrets (JANGAN DI-PUSH KE GITHUB)
|-- .gitignore # Daftar file yang diabaikan oleh Git
|-- requirements.txt # Daftar library Python yang dibutuhkan
|-- README.md # Dokumentasi ini

# Setup & Instalasi

1.  **Clone Repositori**

    ```bash
    git clone <URL_REPO_ANDA>
    cd <NAMA_FOLDER_REPO>
    ```

2.  **Buat Virtual Environment**

    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\Activate.ps1
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Setup Environment Variables**
    Buat file `.env` dari contoh di bawah dan isi dengan kredensial Anda.

    ```ini
    # .env
    WHATSAPP_API_TOKEN="TOKEN_DARI_META"
    WHATSAPP_VERIFY_TOKEN="BUAT_TOKEN_RAHASIA_ANDA"
    WHATSAPP_PHONE_NUMBER_ID="ID_NOMOR_TELEPON_DARI_META"
    ADMIN_PHONE_NUMBER="NOMOR_WA_ADMIN_DENGAN_KODE_NEGARA"
    ```

5.  **Setup Kredensial Google**
    Letakkan file kredensial `client_secret.json` Anda di direktori utama proyek. Pastikan Anda sudah membagikan akses Google Sheet ke email service account.

## Menjalankan Aplikasi

1.  **Jalankan Server FastAPI**

    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Jalankan Ngrok** (di terminal terpisah)
    ```bash
    ngrok http 8000
    ```
3.  **Konfigurasi Webhook**
    Gunakan URL `https` dari ngrok untuk di-setup sebagai URL Callback di dashboard Meta Developer Anda.
