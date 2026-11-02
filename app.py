import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

# --- CONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Tes SPM Online - PT Bumi Mas Wahyu",
    page_icon="🧩",
    layout="centered"
)

RESULTS_FILE = "spm_results.csv"

# --- DEFAULTS & INITIALIZATION ---
if "page" not in st.session_state:
    st.session_state.page = "register"
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# --- NORMA KONVERSI GRADE SPM ---
def calculate_spm_grade(raw_score):
    if raw_score >= 54:
        return "Grade I", "Intellectually Superior (Sangat Tinggi)"
    elif raw_score >= 48:
        return "Grade II+", "Definitely Above Average (Tinggi)"
    elif raw_score >= 42:
        return "Grade II", "Above Average (Di Atas Rata-rata)"
    elif raw_score >= 30:
        return "Grade III", "Intellectually Average (Rata-rata / Normal)"
    elif raw_score >= 20:
        return "Grade IV", "Below Average (Di Bawah Rata-rata)"
    else:
        return "Grade V", "Intellectually Defective (Rendah)"

# --- BANK SOAL SPM (Simulasi Set Matriks) ---
QUESTIONS = [
    {
        "id": 1,
        "set": "Set A",
        "no": "A1",
        "question": "Pilihlah potongan gambar yang paling tepat untuk melengkapi matriks pola di bawah ini:",
        "img_url": "[suspicious link removed]",
        "options": ["Opsi 1", "Opsi 2", "Opsi 3", "Opsi 4", "Opsi 5", "Opsi 6"],
        "correct": "Opsi 4"
    },
    {
        "id": 2,
        "set": "Set A",
        "no": "A2",
        "question": "Perhatikan kontinuitas pola dan garis. Pilih opsi yang sesuai:",
        "img_url": "[suspicious link removed]",
        "options": ["Opsi 1", "Opsi 2", "Opsi 3", "Opsi 4", "Opsi 5", "Opsi 6"],
        "correct": "Opsi 2"
    },
    # Soal disesuaikan hingga Set E (Total 60 soal)
]

# --- HALAMAN 1: REGISTRASI KANDIDAT ---
if st.session_state.page == "register":
    st.title("🏛️ PT Bumi Mas Wahyu")
    st.subheader("Portal Psikotes Online - Standard Progressive Matrices (SPM)")
    st.info("Silakan isi data diri Anda sebelum memulai tes penalaran abstrak.")
    
    with st.form("form_registrasi"):
        nama = st.text_input("Nama Lengkap")
        email = st.text_input("Email")
        no_hp = st.text_input("Nomor WhatsApp/HP")
        posisi = st.selectbox("Posisi yang Dilamar", [
            "Staff Closing (Sales / CS)",
            "Admin Rekrutmen / HR",
            "Supervisor Penjualan",
            "Staff Keuangan / Akuntansi",
            "Arsitek / Site Engineer",
            "Posisi Lainnya"
        ])
        
        btn_start = st.form_submit_button("Mulai Tes SPM 🚀")
        
        if btn_start:
            if not nama or not no_hp or not email:
                st.error("Harap isi seluruh data diri Anda secara lengkap.")
            else:
                st.session_state.user_info = {
                    "nama": nama, "email": email, "no_hp": no_hp,
                    "posisi": posisi, "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.start_time = time.time()
                st.session_state.page = "test"
                st.rerun()

# --- HALAMAN 2: PENGERJAAN TES SPM ---
elif st.session_state.page == "test":
    st.title("🧩 Tes SPM (Standard Progressive Matrices)")
    st.caption(f"Kandidat: **{st.session_state.user_info['nama']}** | Posisi: **{st.session_state.user_info['posisi']}**")
    
    # Timer 30 Menit (1800 detik)
    time_limit = 1800
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(0, time_limit - elapsed)
    mins, secs = divmod(remaining, 60)
    
    st.warning(f"⏱️ **Sisa Waktu:** {mins:02d}:{secs:02d}")
    
    if remaining == 0:
        st.error("⏰ Waktu habis! Jawaban Anda otomatis dikirim.")
        st.session_state.page = "result"
        st.rerun()
        
    with st.form("form_spm_test"):
        for q in QUESTIONS:
            st.markdown(f"### Soal {q['no']} ({q['set']})")
            st.write(q['question'])
            st.image(q['img_url'])
            
            ans = st.radio(
                f"Pilih Jawaban {q['no']}:",
                options=q['options'],
                key=f"q_{q['id']}"
            )
            st.session_state.answers[q['id']] = ans
            st.markdown("---")
            
        btn_submit = st.form_submit_button("Selesaikan Tes 📤")
        if btn_submit:
            st.session_state.page = "result"
            st.rerun()

# --- HALAMAN 3: PENYIMPANAN HASIL ---
elif st.session_state.page == "result":
    st.title("✅ Tes Selesai")
    
    correct_count = sum(1 for q in QUESTIONS if st.session_state.answers.get(q['id']) == q['correct'])
    scaled_raw = int((correct_count / len(QUESTIONS)) * 60)
    grade, category = calculate_spm_grade(scaled_raw)
    
    st.success(f"Terima kasih **{st.session_state.user_info['nama']}**, tes Anda telah tersimpan.")
    
    # Simpan Hasil ke Database CSV HR
    result_data = {
        **st.session_state.user_info,
        "raw_score": scaled_raw,
        "grade": grade,
        "kategori": category
    }
    df_new = pd.DataFrame([result_data])
    
    if os.path.exists(RESULTS_FILE):
        df_final = pd.concat([pd.read_csv(RESULTS_FILE), df_new], ignore_index=True)
    else:
        df_final = df_new
        
    df_final.to_csv(RESULTS_FILE, index=False)
    st.info("💾 Data hasil tes otomatis terhubung dengan database rekrutmen terpusat PT Bumi Mas Wahyu.")
