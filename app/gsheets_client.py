# app/gsheets_client.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Setup Koneksi ---
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
sheet = None

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("RSVP (Responses)")
    sheet = spreadsheet.worksheet("TRANSAKSI_PENGIRIMAN")
    print("Koneksi ke Google Sheet 'TRANSAKSI_PENGIRIMAN' berhasil.")
except Exception as e:
    print(f"Koneksi ke Google Sheets GAGAL: {e}")

# --- Fungsi-fungsi ---

def find_order_by_phone(phone_number: str):
    """Mencari pesanan berdasarkan Nomor HP."""
    if not sheet: return None
    try:
        all_records = sheet.get_all_records()
        for record in reversed(all_records):
            if str(record.get('Nomor HP')) == phone_number:
                return record
        return None
    except Exception as e:
        print(f"Error saat membaca dari GSheet: {e}")
        return None

def write_order(data: dict):
    """Menulis data pesanan dari WhatsApp sesuai urutan kolom baru."""
    if not sheet: return False
    try:
        now = datetime.now()
        order_id = "BOT-" + now.strftime("%Y%m%d%H%M%S")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Menyusun baris sesuai urutan kolom di 'TRANSAKSI_PENGIRIMAN'
        new_row = [
            order_id,                   # A: ID_Kirim
            timestamp,                  # B: Data pembuatan
            data.get('nomor_hp'),       # C: Nomor HP (dari kolom yang Anda tambahkan)
            data.get('nama'),           # D: Nama_Peternak
            data.get('jenis_hewan'),    # E: Jenis_Ternak
            None,                       # F: Jumlah_Ekor (bot tidak menanyakan ini)
            None,                       # G: ID_Rute (bot tidak menanyakan ini)
            data.get('lokasi_jemput'),  # H: Lokasi Jemput (dari kolom yang Anda tambahkan)
            data.get('lokasi_tujuan'),  # I: Lokasi Tujuan (dari kolom yang Anda tambahkan)
            data.get('jadwal'),         # J: Tanggal yang diajukan
            'Menunggu Jadwal',          # K: Status (default)
            'WhatsApp Bot'              # L: input source
            # Tambahkan None jika ada kolom lain setelah ini
        ]
        sheet.append_row(new_row)
        return True
    except Exception as e:
        print(f"Error saat menulis ke GSheet: {e}")
        return False