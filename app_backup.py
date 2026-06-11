import streamlit as st
import pandas as pd
import numpy as np
from ModelFKNN import FuzzyKnn

st.set_page_config(
    page_title="Sistem Pakar Edamame",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 Sistem Pakar Diagnosa Penyakit Tanaman Edamame")
st.write("Sistem ini menggunakan metode Fuzzy K-Nearest Neighbor untuk mendiagnosa penyakit berdasarkan gejala.")

# =========================
# LOAD DATASET
# =========================
@st.cache_data
def load_data():
    data = pd.read_csv("dataset_edamame.csv", sep=";")
    return data

data = load_data()

X = data.iloc[:, :-1].values
y = data.iloc[:, -1].astype(str).values
gejala_list = data.columns[:-1].tolist()

# =========================
# TRAIN MODEL
# =========================
@st.cache_resource
def train_model():
    model = FuzzyKnn(k=3)
    model.fit(X, y)
    return model

model = train_model()

# =========================
# DESKRIPSI PENYAKIT
# =========================
deskripsi_penyakit = {
    "Rhizoctonia": "Rhizoctonia biasanya menyerang akar dan pangkal batang, menyebabkan tanaman layu dan pertumbuhan terhambat.",
    "Pythium sp": "Pythium sp sering menyebabkan busuk akar, akar mudah rusak, dan tanaman rebah terutama pada kondisi tanah terlalu lembap.",
    "Fusarium": "Fusarium dapat menyebabkan tanaman layu, daun menguning, dan gangguan pada jaringan pembuluh tanaman.",
    "Karat Daun": "Karat daun ditandai dengan bercak seperti karat pada permukaan daun.",
    "Doreng Hawar Bacteria": "Penyakit bakteri ini dapat menyebabkan bercak basah, hawar, dan kerusakan jaringan daun.",
    "Colletotrichum": "Colletotrichum biasanya menyebabkan bercak nekrotik dan luka pada daun atau batang.",
    "Bercak Daun": "Bercak daun ditandai dengan munculnya bercak-bercak pada daun yang dapat melebar.",
    "Sclerotium Rolfsii": "Sclerotium rolfsii menyerang pangkal batang dan akar, sering menyebabkan busuk pangkal batang."
}

saran_penyakit = {
    "Rhizoctonia": "Kurangi kelembapan berlebih, gunakan media tanam sehat, dan lakukan sanitasi lahan.",
    "Pythium sp": "Perbaiki drainase, hindari penyiraman berlebihan, dan gunakan benih sehat.",
    "Fusarium": "Gunakan varietas tahan, rotasi tanaman, dan hindari penggunaan tanah yang sudah terinfeksi.",
    "Karat Daun": "Pangkas daun terinfeksi dan jaga sirkulasi udara.",
    "Doreng Hawar Bacteria": "Hindari percikan air berlebih dan buang bagian tanaman yang sakit.",
    "Colletotrichum": "Kurangi kelembapan, bersihkan sisa tanaman sakit, dan lakukan pengamatan rutin.",
    "Bercak Daun": "Buang daun yang terinfeksi dan hindari kelembapan daun terlalu lama.",
    "Sclerotium Rolfsii": "Cabut tanaman parah, bersihkan lahan, dan hindari genangan air."
}

# =========================
# RESET FUNCTION
# =========================
def reset_gejala():
    for gejala in gejala_list:
        st.session_state[gejala] = False

# =========================
# INISIALISASI STATE
# =========================
for gejala in gejala_list:
    if gejala not in st.session_state:
        st.session_state[gejala] = False

# =========================
# INPUT GEJALA
# =========================
st.subheader("📝 Pilih Gejala yang Terlihat")

selected_gejala = []

cols = st.columns(2)

for i, gejala in enumerate(gejala_list):
    with cols[i % 2]:
        cek = st.checkbox(
            gejala,
            key=gejala
        )
        selected_gejala.append(1 if cek else 0)

# =========================
# TOMBOL
# =========================
col1, col2 = st.columns(2)

with col1:
    diagnosa = st.button("🔍 Diagnosa Penyakit")

with col2:
    st.button(
        "🔄 Reset Gejala",
        on_click=reset_gejala
    )

# =========================
# DIAGNOSA
# =========================
if diagnosa:
    if sum(selected_gejala) == 0:
        st.warning("Silakan pilih minimal satu gejala terlebih dahulu.")
    else:
        input_data = np.array([selected_gejala])

        hasil = model.predict(input_data)[0]

        st.success(f"Hasil Diagnosis: {hasil}")
        st.subheader("📌 Gejala yang Dipilih")
        gejala_terpilih = [gejala_list[i] for i, val in enumerate(selected_gejala) if val == 1]

        for g in gejala_terpilih:
            st.write(f"- {g}")

        st.subheader("📖 Deskripsi Penyakit")
        st.info(deskripsi_penyakit.get(hasil, "Deskripsi penyakit belum tersedia."))

        st.subheader("💡 Saran Penanganan")
        st.write(saran_penyakit.get(hasil, "Saran penanganan belum tersedia."))

# =========================
# DATASET
# =========================
with st.expander("📊 Lihat Dataset"):
    st.dataframe(data)