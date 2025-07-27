import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Setup Koneksi ---

# Definisikan scope atau cakupan akses API
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']

try:
    # Otorisasi menggunakan file kunci JSON
    creds = ServiceAccountCredentials.from_json_keyfile_name('../client_secret.json', scope)
    client = gspread.authorize(creds)

    # Buka spreadsheet berdasarkan namanya. Ganti "NamaSheetAnda" dengan nama sheet Anda.
    # Pastikan sheet pertama (Sheet1) adalah sheet yang akan digunakan.
    sheet = client.open("Angkut Ternak Orders").sheet1
    print("Koneksi ke Google Sheets berhasil.")

except Exception as e:
    print(f"Koneksi ke Google Sheets GAGAL: {e}")
    sheet = None

# --- Fungsi-fungsi ---

def find_order_by_phone(phone_number: str):
    """
    Mencari baris pesanan terakhir berdasarkan nomor telepon.
    Asumsi: Baris pertama di sheet adalah header (misal: "Nomor HP", "Nama", "Status").
    """
    if not sheet:
        return None
        
    try:
        # Mengambil semua baris sebagai list of dictionaries
        all_records = sheet.get_all_records()
        
        # Loop dari belakang untuk mendapatkan pesanan terbaru
        for record in reversed(all_records):
            # Pastikan nama kolom di GSheet Anda "Nomor HP"
            if str(record.get('Nomor HP')) == phone_number:
                print(f"Pesanan ditemukan untuk {phone_number}: {record}")
                return record # Kembalikan data pesanan jika ditemukan
        
        print(f"Tidak ada pesanan ditemukan untuk {phone_number}")
        return None # Kembalikan None jika tidak ada

    except Exception as e:
        print(f"Error saat membaca dari GSheet: {e}")
        return None

def write_order(data: dict):
    """
    Menulis data pesanan baru ke baris terakhir di sheet.
    Penting: Urutan kolom di sheet harus sesuai dengan urutan data di dictionary.
    """
    if not sheet:
        return False
        
    try:
        # Ubah dictionary menjadi list untuk ditulis ke sheet
        row = list(data.values())
        sheet.append_row(row)
        print(f"Data berhasil ditulis ke GSheet: {row}")
        return True
    except Exception as e:
        print(f"Error saat menulis ke GSheet: {e}")
        return False