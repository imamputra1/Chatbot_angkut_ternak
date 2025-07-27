# app/main.py

import os
import json
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

# NEW: Kita siapkan impor untuk langkah selanjutnya, tapi kita beri komentar dulu
from gsheets_client import find_order_by_phone, write_order

# --- Setup Awal ---
load_dotenv()
app = FastAPI(title="WhatsApp Chatbot Server")

# Kredensial dari .env
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")

# Kamus untuk menyimpan sesi percakapan (state management sederhana)
user_sessions = {}

# --- Helper Functions ---

# NEW: Fungsi terpisah untuk logika pengecekan status
async def check_and_reply_status(phone_number: str):
    """Mencari pesanan dan membalas dengan statusnya."""
    print(f"Mencari pesanan untuk nomor: {phone_number}")
    
    # TODO: Panggil fungsi dari gsheets_client.py saat sudah siap
    # Untuk sekarang, kita simulasikan hasilnya
    # order = find_order_by_phone(phone_number) 
    order = None # Hapus baris ini saat gsheets_client sudah siap

    if order:
        # Jika pesanan ditemukan
        status_message = (
            f"Pesanan Anda ditemukan:\n\n"
            f"Nama: {order.get('Nama')}\n"
            f"Jenis Hewan: {order.get('Jenis Hewan')}\n"
            f"Jadwal: {order.get('Jadwal')}\n"
            f"Status: *{order.get('Status')}*"
        )
        await send_whatsapp_message(phone_number, status_message)
    else:
        # Jika pesanan tidak ditemukan
        not_found_message = "Maaf, tidak ada pesanan dari nomor Anda. Silakan hubungi admin kami jika terjadi kesalahan."
        await send_whatsapp_message(phone_number, not_found_message)

# --- Endpoint & Logic ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Server is running"}


@app.get("/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED")
        return Response(content=challenge, media_type="text/plain", status_code=200)

    raise HTTPException(status_code=403, detail="Verification token is invalid.")


@app.post("/webhook")
async def handle_message(request: Request):
    """Menerima dan memproses pesan masuk dari user."""
    payload = await request.json()
    print("--- Incoming Payload ---")
    print(json.dumps(payload, indent=2))

    try:
        changes = payload.get("entry", [])[0].get("changes", [])[0]
        message_data = changes.get("value", {}).get("messages", [{}])[0]

        if message_data.get("type") == "text":
            from_number = message_data.get("from")
            msg_body = message_data.get("text", {}).get("body").strip() # .strip() untuk hapus spasi

            if from_number not in user_sessions:
                # MODIFIED: Berikan menu pilihan ke pengguna baru
                user_sessions[from_number] = {'step': 'awaiting_menu_choice', 'data': {}}
                menu_text = (
                    "Selamat datang di layanan Angkut Ternak!\n\n"
                    "Silakan balas dengan angka untuk memilih:\n"
                    "1. Buat Pesanan Baru\n"
                    "2. Cek Status Pesanan"
                )
                await send_whatsapp_message(from_number, menu_text)
            else:
                session = user_sessions[from_number]
                current_step = session['step']

                # NEW: Blok logika untuk menangani pilihan menu
                if current_step == 'awaiting_menu_choice':
                    if msg_body == '1':
                        session['step'] = 'awaiting_name'
                        await send_whatsapp_message(from_number, "Baik, mari kita mulai pesanan baru. Siapa nama Anda?")
                    elif msg_body == '2':
                        await check_and_reply_status(from_number)
                        del user_sessions[from_number] # Hapus sesi setelah cek status
                    else:
                        await send_whatsapp_message(from_number, "Pilihan tidak valid. Mohon balas dengan angka 1 atau 2.")

                elif current_step == 'awaiting_name':
                    session['data']['nama'] = msg_body
                    session['step'] = 'awaiting_pet_type'
                    await send_whatsapp_message(from_number, f"Halo {msg_body}! Selanjutnya, apa jenis hewan yang akan diangkut?")
                
                # ... sisa logika elif untuk buat pesanan tetap sama ...

                elif current_step == 'awaiting_pet_type':
                    session['data']['jenis_hewan'] = msg_body
                    session['step'] = 'awaiting_location'
                    await send_whatsapp_message(from_number, "Baik, jenis hewan sudah dicatat. Mohon info lokasi penjemputan.")

                elif current_step == 'awaiting_location':
                    session['data']['lokasi_jemput'] = msg_body
                    session['step'] = 'awaiting_destination'
                    await send_whatsapp_message(from_number, "Lokasi penjemputan dicatat. Mohon info lokasi tujuan.")

                elif current_step == 'awaiting_destination':
                    session['data']['lokasi_tujuan'] = msg_body
                    session['step'] = 'awaiting_datetime'
                    await send_whatsapp_message(from_number, "Lokasi tujuan dicatat. Terakhir, mohon info tanggal dan jam penjemputan.")

                elif current_step == 'awaiting_datetime':
                    session['data']['jadwal'] = msg_body
                    
                    # PENTING: Tambahkan nomor HP ke data yang akan disimpan
                    session['data']['nomor_hp'] = from_number

                    # --- FINALISASI ---
                    order_data = session['data']
                    summary_text = (
                        f"Pesanan baru telah dikonfirmasi:\n\n"
                        f"Nama: {order_data.get('nama')}\n"
                        f"Jenis Hewan: {order_data.get('jenis_hewan')}\n"
                        f"Lokasi Jemput: {order_data.get('lokasi_jemput')}\n"
                        f"Lokasi Tujuan: {order_data.get('lokasi_tujuan')}\n"
                        f"Jadwal: {order_data.get('jadwal')}\n"
                        f"Dari No HP: {order_data.get('nomor_hp')}"
                    )
                    
                    # Kirim konfirmasi ke pengguna
                    await send_whatsapp_message(from_number, f"Terima kasih! Pesanan Anda sudah kami terima.\n\nBerikut ringkasannya:\n{summary_text}")
                    
                    # PANGGIL FUNGSI UNTUK MENYIMPAN & NOTIFIKASI ADMIN
                    write_order(order_data)
                    if ADMIN_PHONE_NUMBER:
                        await send_whatsapp_message(ADMIN_PHONE_NUMBER, summary_text)

                    # Hapus sesi pengguna untuk memulai dari awal lagi nanti
                    del user_sessions[from_number]
    except Exception as e:
        print(f"[ERROR] Could not process webhook: {e}")
        return Response(status_code=200)

    return Response(status_code=200)


async def send_whatsapp_message(recipient_id: str, message: str):
    """Fungsi untuk mengirim pesan balasan via WhatsApp Cloud API."""
    if not WHATSAPP_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print(f"[WARNING] WhatsApp credentials not set. Cannot send message to {recipient_id}.")
        print(f"Message: {message}")
        return

    api_url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_API_TOKEN}"}
    payload = {"messaging_product": "whatsapp", "to": recipient_id, "text": {"body": message}}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Message sent to {recipient_id}, status: {response.status_code}")
        except httpx.HTTPStatusError as e:
            print(f"[ERROR] Failed to send message: {e.response.text}")