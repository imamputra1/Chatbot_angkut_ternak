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
    """Mencari baris pesanan terakhir berdasarkan nomor telepon."""
    if not sheet:
        return None

    try:
        all_records = sheet.get_all_records()
        print(f"--- DEBUG: Mencari nomor '{phone_number}' (Tipe: {type(phone_number)}) ---")

        for record in reversed(all_records):
            # Ambil nomor dari sheet
            sheet_phone_number = record.get('Nomor HP')

            # Tampilkan apa yang sebenarnya dibaca dari sheet sebelum konversi
            print(f"Membaca baris: Nomor dari Sheet = '{sheet_phone_number}' (Tipe: {type(sheet_phone_number)})")

            # Lakukan perbandingan
            if str(sheet_phone_number) == phone_number:
                print("--- DEBUG: KECOCOKAN DITEMUKAN! ---")
                return record

        print("--- DEBUG: TIDAK ADA KECOCOKAN. Pencarian Selesai. ---")
        return None

    except Exception as e:
        print(f"Error saat membaca dari GSheet: {e}")
        return None

# app/gsheets_client.py

def write_order(data: dict):
    """Menulis data pesanan dari WhatsApp sesuai urutan kolom final."""
    if not sheet: return False
    try:
        now = datetime.now()
        order_id = "BOT-" + now.strftime("%Y%m%d%H%M%S")
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Menambahkan placeholder 'None' untuk kolom 'Nama Driver'
        # Pastikan urutan ini cocok dengan urutan kolom di Google Sheet Anda
        new_row = [
            order_id,                   # ID_Kirim
            timestamp,                  # Data pembuatan
            data.get('nomor_hp'),       # Nomor HP
            data.get('nama'),           # Nama_Peternak
            data.get('jenis_hewan'),    # Jenis_Ternak
            data.get('jumlah_ekor'),    # Jumlah_Ekor
            data.get('lokasi_jemput'),  # Lokasi Jemput
            data.get('lokasi_tujuan'),  # Lokasi Tujuan
            data.get('jadwal'),         # Tanggal yang diajukan
            'Menunggu Jadwal',          # Status
            None,                       # Nama Driver (diisi admin nanti)
            'WhatsApp Bot',             # input source
            None                        # Biaya pengiriman (diisi admin nanti)
        ]
        sheet.append_row(new_row)
        print(f"Data berhasil ditulis ke GSheet dengan urutan benar: {new_row}")
        return True
    except Exception as e:
        print(f"Error saat menulis ke GSheet: {e}")
        return False