import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL (PENTING! UBAH SESUAI KEBUTUHAN ANDA)
# ==============================================================================

# Mengambil API key dari Streamlit Secrets atau variabel lingkungan.
# Lebih aman daripada menuliskannya langsung di kode.
# Caranya: Buat file .streamlit/secrets.toml di repo GitHub Anda.
# Isinya: API_KEY = "AIza..."
try:
    API_KEY = st.secrets["API_KEY"]
except KeyError:
    st.error("Peringatan: API Key belum diatur. Harap tambahkan `API_KEY` ke Streamlit Secrets.")
    st.stop()

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
# Ini adalah "instruksi sistem" yang akan membuat chatbot berperilaku sesuai keinginan Anda.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah ahli fisika. Tuliskan rumus tentang Fisika. Jawaban singkat. Tolak pertanyaan non-fisika."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan rumus yang ingin anda ketahui."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Ahli Fisika Chatbot", page_icon="⚛️")
st.title("Chatbot Ahli Fisika ⚛️")
st.caption("🤖 Bot ini akan menjawab pertanyaan tentang rumus fisika. Ketik pertanyaan Anda di bawah.")

# Inisialisasi Gemini API
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4, 
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi atau menginisialisasi Gemini: {e}")
    st.stop()

# Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Tampilkan riwayat chat sebelumnya
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["parts"][0])
    elif message["role"] == "model":
        with st.chat_message("assistant"):
            st.markdown(message["parts"][0])

# Menerima input dari pengguna
if prompt := st.chat_input("Tanyakan rumus fisika..."):
    # Tampilkan pesan pengguna
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari model
    try:
        chat_history = [
            {"role": msg["role"], "parts": [msg["parts"][0]]} 
            for msg in st.session_state.messages
        ]
        
        response = model.generate_content(chat_history)
        
        if response and response.text:
            model_response = response.text
        else:
            model_response = "Maaf, saya tidak bisa memberikan balasan."

    except Exception as e:
        model_response = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}"

    # Tampilkan respons model
    st.session_state.messages.append({"role": "model", "parts": [model_response]})
    with st.chat_message("assistant"):
        st.markdown(model_response)
