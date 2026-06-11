import streamlit as st
import pandas as pd
import numpy as np
from ModelFKNN import FuzzyKnn
from database import (
    create_tables,
    get_dataset,
    tambah_dataset_csv,
    simpan_riwayat_diagnosa,
    get_riwayat_diagnosa,
    get_riwayat_saya,
    get_detail_riwayat,
    validasi_riwayat,
    tolak_riwayat,
    check_login,
    get_admin,
    tambah_admin,
    ubah_password_admin,
    tambah_penyakit,
    edit_penyakit,
    get_penyakit,
    nonaktifkan_penyakit,
    tambah_dataset,
    get_dataset_with_id, hapus_dataset_by_ids,
    edit_gejala,
    tambah_gejala,
    get_gejala,
    nonaktifkan_gejala
)
st.set_page_config(
    page_title="Sistem Pakar Edamame",
    page_icon="🌱",
    layout="wide"
)
# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
.stApp {
    background-color: #061B18;
    color: #F4FFF8;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B8F83, #07635C);
    border-right: 1px solid rgba(255,255,255,0.12);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

h1, h2, h3 {
    color: #F4FFF8;
}

p, label, span, div {
    color: #E8FFF3;
}

.stButton > button {
    background-color: #18B985;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1rem;
    font-weight: 700;
}

.stButton > button:hover {
    background-color: #22D39A;
    color: white;
}

[data-testid="stMetric"],
div[data-testid="stExpander"],
.stAlert {
    background-color: #0B2A25;
    border-radius: 14px;
    border: 1px solid rgba(120,255,190,0.15);
}

.stTextInput input,
.stTextArea textarea {
    background-color: #0B2A25;
    color: white;
    border-radius: 10px;
    border: 1px solid #1E7F68;
}

.stSelectbox div[data-baseweb="select"] {
    background-color: #0B2A25;
    color: white;
}

.stCheckbox {
    background-color: #0B2A25;
    padding: 8px 12px;
    border-radius: 10px;
    margin-bottom: 6px;
    border: 1px solid rgba(120,255,190,0.12);
}
</style>
""", unsafe_allow_html=True)


# =========================
# SESSION LOGIN
# =========================
if "login_admin" not in st.session_state:
    st.session_state.login_admin = False


# =========================
# LOAD DATA
# =========================

create_tables()

@st.cache_data
def load_data():
    return get_dataset()

data = load_data()

gejala_df = get_gejala()
kolom_gejala = gejala_df["kode_gejala"].tolist()
for col in kolom_gejala:
    if col not in data.columns:
        data[col] = 0
X = data[kolom_gejala].apply(
    pd.to_numeric,
    errors="coerce"
).fillna(0).astype(int).values

y = data["penyakit"].astype(str).values

gejala_list = kolom_gejala

@st.cache_resource
def train_model():
    model = FuzzyKnn(k=3)
    model.fit(X, y)
    return model

model = train_model()

# =========================
# RESET GEJALA
# =========================
def reset_diagnosa():

    gejala_df = get_gejala()

    for _, row in gejala_df.iterrows():

        kode = row["kode_gejala"]

        st.session_state[kode] = False

    # HAPUS HASIL DIAGNOSA
    if "hasil_diagnosa" in st.session_state:
        del st.session_state["hasil_diagnosa"]

for gejala in gejala_list:
    if gejala not in st.session_state:
        st.session_state[gejala] = False

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown("""
    <h1 style='text-align: center; color: #2E8B57;'>
        🌱 Edamame Expert
    </h1>
    """, unsafe_allow_html=True)

    st.caption("Sistem Pakar Diagnosa Penyakit Tanaman Edamame")

    st.divider()

    if "menu" not in st.session_state:
        st.session_state.menu = "🏠 Beranda"

    # =========================
    # MENU UMUM
    # =========================

    if st.button("🏠 Beranda", use_container_width=True):
        st.session_state.menu = "🏠 Beranda"

    if st.button("🔍 Diagnosa", use_container_width=True):
        st.session_state.menu = "🔍 Diagnosa"

    if st.button("🌿 Jenis Penyakit", use_container_width=True):
        st.session_state.menu = "🌿 Jenis Penyakit"

    st.divider()

    # =========================
    # JIKA SUDAH LOGIN
    # =========================

    if st.session_state.get("login_admin", False):

        role = st.session_state.get("role")

        st.success(
            f"🟢 Login sebagai {role}"
        )
        with st.expander("🔑 Ubah Password"):

            password_lama = st.text_input(
                "Password Lama",
                type="password",
                key="sidebar_password_lama"
            )

            password_baru = st.text_input(
                "Password Baru",
                type="password",
                key="sidebar_password_baru"
            )

            konfirmasi_password = st.text_input(
                "Konfirmasi Password Baru",
                type="password",
                key="sidebar_konfirmasi_password"
            )

            if st.button("💾 Simpan Password", use_container_width=True):

                if password_lama == "" or password_baru == "" or konfirmasi_password == "":
                    st.warning("Semua field password wajib diisi.")

                elif password_baru != konfirmasi_password:
                    st.warning("Konfirmasi password tidak sama.")

                else:
                    berhasil = ubah_password_admin(
                        st.session_state.username,
                        password_lama,
                        password_baru
                    )

                    if berhasil:
                        st.success("Password berhasil diubah.")
                    else:
                        st.error("Password lama salah.")
        # =========================
        # STAFF
        # =========================

        if role == "staff":

            if st.button(
                "📋 Riwayat Saya",
                use_container_width=True
            ):
                st.session_state.menu = "📋 Riwayat Saya"

        # =========================
        # PAKAR
        # =========================

        elif role == "pakar":

            if st.button(
                "⚙️ Admin Panel",
                use_container_width=True
            ):
                st.session_state.menu = "⚙️ Admin Panel"

            if st.button(
                "📋 Riwayat Diagnosa",
                use_container_width=True
            ):
                st.session_state.menu = "📋 Riwayat Diagnosa"

        # =========================
        # LOGOUT
        # =========================

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            st.session_state.login_admin = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.menu = "🏠 Beranda"

            st.rerun()

    # =========================
    # BELUM LOGIN
    # =========================

    else:

        st.info("🔒 Belum Login")

        if st.button(
            "🔐 Login",
            use_container_width=True
        ):
            st.session_state.menu = "🔐 Login Admin"

    st.divider()

    st.caption("© Sistem Pakar Edamame FKNN")
# menu aktif
menu = st.session_state.menu

# POP UP dialog
@st.dialog("⚠️ Konfirmasi Hapus Dataset")
def popup_hapus_dataset():
    
    jumlah = len(st.session_state.dataset_hapus_ids)

    st.warning(f"Anda akan menghapus {jumlah} data dataset.")
    st.write("Data yang sudah dihapus tidak dapat dikembalikan.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Ya, Hapus"):
            hapus_dataset_by_ids(st.session_state.dataset_hapus_ids)

            st.cache_data.clear()
            st.cache_resource.clear()

            st.success("Dataset terpilih berhasil dihapus.")

            del st.session_state["dataset_hapus_ids"]

            st.rerun()

    with col2:
        if st.button("❌ Batal"):
            del st.session_state["dataset_hapus_ids"]
            st.rerun()
if "dataset_hapus_ids" in st.session_state:
    popup_hapus_dataset()
@st.dialog("🔎 Detail Diagnosa")
def detail_riwayat_dialog():
    id_riwayat = st.session_state.id_detail_riwayat
    
    detail = get_detail_riwayat(id_riwayat)
    if detail is None:
        st.error("Data riwayat tidak ditemukan.")
        return
    penyakit_df = get_penyakit()
    kode_aktif = penyakit_df["kode_penyakit"].tolist()
    penyakit_masih_aktif = (
    detail["hasil_kode"] in kode_aktif
    )
    kecocokan=detail['nilai_keanggotaan']*100

    st.write(f"**Tanggal:** {detail['tanggal']}")
    st.write(f"**Username:** {detail['username']}")
    st.write(f"**Role:** {detail['role']}")
    st.write(f"**Hasil Diagnosis:** {detail['hasil_penyakit']}")
    st.write(f"**Kode Penyakit:** {detail['hasil_kode']}")
    st.write(f"**Tingkat Keyakinan:** {kecocokan:.2f}%")
    st.write(f"**Status:** {detail['status']}")

    st.subheader("🩺 Gejala yang Dipilih")
    st.write(detail["gejala_dipilih"])

    if not penyakit_masih_aktif:
        st.warning(
            "Penyakit pada riwayat ini sudah nonaktif sehingga tidak dapat dijadikan data training."
        )
    elif detail["status"] == "menunggu":
        # tombol Jadikan Data Training dan Tolak
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Jadikan Data Training"):
                berhasil = validasi_riwayat(id_riwayat)

                if berhasil:
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.success("Riwayat berhasil dijadikan data training.")
                    st.rerun()
                else:
                    st.error("Gagal memvalidasi riwayat.")

        with col2:
            if st.button("❌ Tolak Diagnosa"):
                tolak_riwayat(id_riwayat)
                st.success("Riwayat berhasil ditolak.")
                st.rerun()
    else:
        st.info("Riwayat ini sudah divalidasi.")
@st.dialog("✅ Riwayat Tersimpan")
def popup_riwayat_tersimpan():

    st.success("Riwayat diagnosa berhasil disimpan.")
    st.write("Data diagnosa sudah masuk ke riwayat dan menunggu validasi pakar.")

    if st.button("Tutup"):

        if "hasil_diagnosa" in st.session_state:
            del st.session_state["hasil_diagnosa"]

        st.session_state.popup_riwayat = False

        st.rerun()
        
@st.dialog("🔎 Detail Diagnosa")
def detail_riwayat_staff():
    id_riwayat = st.session_state.id_detail_riwayat
    
    detail = get_detail_riwayat(id_riwayat)
    if detail is None:
        st.error("Data tidak ditemukan.")
        return
    penyakit_df = get_penyakit()
    kode_aktif = penyakit_df["kode_penyakit"].tolist()
    penyakit_masih_aktif = (
    detail["hasil_kode"] in kode_aktif
    )
    keyakinan=detail["nilai_keanggotaan"]*100

    st.write(f"**Tanggal:** {detail['tanggal']}")
    st.write(f"**Hasil Diagnosis:** {detail['hasil_penyakit']}")
    st.write(f"**Tingkat Keyakinan:** {keyakinan:.2f}%")
    if not penyakit_masih_aktif:
        st.warning(
            "Penyakit pada riwayat ini sudah nonaktif sehingga tidak dapat dijadikan data training."
        )   
    else: 
        st.write(f"**Status:** {detail['status']}")

    st.subheader("🩺 Gejala yang Dipilih")

    st.write(detail["gejala_dipilih"])
# =========================
# BERANDA
# =========================
if menu == "🏠 Beranda":
    st.title("🌱 Sistem Pakar Diagnosa Penyakit Tanaman Edamame")
    st.write("""
    Sistem ini digunakan untuk membantu mendiagnosa penyakit tanaman edamame
    berdasarkan gejala yang dipilih oleh pengguna.

    Metode yang digunakan adalah **Fuzzy K-Nearest Neighbor (FKNN)**.
    """)

# =========================
# DIAGNOSA
# =========================
elif menu == "🔍 Diagnosa":
    st.title("🔍 Diagnosa Penyakit Edamame")
    st.write("Pilih gejala yang terlihat pada tanaman edamame.")
    gejala_df = get_gejala()
    selected_gejala = []
    cols = st.columns(2)
    for i, row in gejala_df.iterrows():
        kode = row["kode_gejala"]
        nama = row["nama_gejala"]

        with cols[i % 2]:
            cek = st.checkbox(nama, key=kode)
            selected_gejala.append(1 if cek else 0)

    col1, col2 = st.columns(2)

    with col1:
        diagnosa = st.button("🔍 Diagnosa Penyakit")

    with col2:
        st.button("🔄 Reset Diagnosa", on_click=reset_diagnosa)

    if diagnosa:
        if sum(selected_gejala) == 0:
            st.warning("Silakan pilih minimal satu gejala terlebih dahulu.")
        else:
            input_data = np.array([selected_gejala])
            top_penyakit = model.predict_top_membership(input_data)[0]

            hasil_kode = top_penyakit[0][0]
            nilai_utama = top_penyakit[0][1]

            penyakit_df = get_penyakit()
            data_hasil = penyakit_df[penyakit_df["kode_penyakit"] == hasil_kode]

            gejala_terpilih = []

            for i, value in enumerate(selected_gejala):
                if value == 1:
                    nama_gejala = gejala_df.iloc[i]["nama_gejala"]
                    gejala_terpilih.append(nama_gejala)

            if data_hasil.empty:
                hasil_penyakit = hasil_kode
                deskripsi = "Detail penyakit belum tersedia di database."
                penanganan = "-"
            else:
                data_hasil = data_hasil.iloc[0]
                hasil_penyakit = data_hasil["nama_penyakit"]
                deskripsi = data_hasil["deskripsi"]
                penanganan = data_hasil["penanganan"]

            st.session_state.hasil_diagnosa = {
                "selected_gejala": selected_gejala,
                "gejala_terpilih": gejala_terpilih,
                "hasil_kode": hasil_kode,
                "hasil_penyakit": hasil_penyakit,
                "nilai_utama": nilai_utama,
                "top_penyakit": top_penyakit[:3],
                "deskripsi": deskripsi,
                "penanganan": penanganan
            }

    if "hasil_diagnosa" in st.session_state:
        hasil = st.session_state.hasil_diagnosa
        nilai = hasil["nilai_utama"]
        persentase = nilai*100

        # st.success(f"🌱 Hasil Diagnosis: **{hasil['hasil_penyakit']}**")
        st.subheader(f"🌱 {hasil['hasil_penyakit']}")

        st.progress(min(hasil["nilai_utama"], 1.0))

        st.markdown(
            f"""
            <div style="
                font-size:32px;
                font-weight:bold;
                margin-top:-10px;
            ">
                {persentase:.2f}%
            </div>
            """,
            unsafe_allow_html=True
        )
        if nilai >= 0.75:
            st.success("🟢 Tingkat Keyakinan: Tinggi")
        elif nilai >= 0.40:
            st.info("🔵 Tingkat Keyakinan: Sedang")
        else:
            st.warning("🟡 Tingkat Keyakinan: Rendah. Disarankan konfirmasi pakar.")

        st.subheader("📖 Deskripsi Penyakit")
        st.info(hasil["deskripsi"])

        st.subheader("💡 Penanganan")
        st.write(hasil["penanganan"])

        st.subheader("📌 Gejala yang Dipilih")
        for nama in hasil["gejala_terpilih"]:
            st.write(f"- {nama}")
            
        st.subheader("📊 Kemungkinan Penyakit Lain")

        penyakit_df = get_penyakit()

        for urutan, (kode, nilai) in enumerate(hasil["top_penyakit"][1:], start=2):
            data_alt = penyakit_df[penyakit_df["kode_penyakit"] == kode]

            if data_alt.empty:
                nama_alt = kode
            else:
                nama_alt = data_alt.iloc[0]["nama_penyakit"]
            persen = nilai*100
            st.write(f"{urutan}. **{nama_alt} ({kode})** — Kecocokan : `{persen:.2f}`%")
        st.divider()

        if st.session_state.get("login_admin", False):
            if st.button("💾 Simpan Riwayat Diagnosa"):
                status = "diterima" if hasil["nilai_utama"] >= 0.75 else "menunggu"
                id_riwayat = simpan_riwayat_diagnosa(
                    username=st.session_state.get("username", "admin"),
                    role=st.session_state.get("role", "pakar"),
                    data_gejala=hasil["selected_gejala"],
                    gejala_dipilih=hasil["gejala_terpilih"],
                    hasil_kode=hasil["hasil_kode"],
                    hasil_penyakit=hasil["hasil_penyakit"],
                    nilai_keanggotaan=hasil["nilai_utama"],
                    status=status
                )
                if status == "diterima":
                    tambah_dataset(
                        hasil["selected_gejala"],
                        hasil["hasil_kode"]
                    )

                    st.cache_data.clear()
                    st.cache_resource.clear()
                popup_riwayat_tersimpan()
               
        else:
            st.info("🔒 Login sebagai staff atau pakar untuk menyimpan riwayat diagnosa.")
                    
# =========================
# JENIS PENYAKIT
# =========================
elif menu == "🌿 Jenis Penyakit":
    st.title("🌿 Jenis-Jenis Penyakit Edamame")
    penyakit_df = get_penyakit()
    if penyakit_df.empty:
        st.warning("Belum ada data penyakit.")
    else:
        for _, row in penyakit_df.iterrows():
            with st.expander(row["nama_penyakit"]):
                st.write("**Deskripsi / Gejala Umum:**")
                st.write(row["deskripsi"])

                st.write("**Penanganan:**")
                st.write(row["penanganan"])
# =========================
# LOGIN ADMIN
# =========================
elif menu == "🔐 Login Admin":
    st.title("🔐 Login Admin")

    if st.session_state.login_admin:
        st.success("✅ Anda sudah login.")
        st.info(f"Username: {st.session_state.username}")
        st.info(f"Role: {st.session_state.role}")

        if st.button("🚪 Logout"):
            st.session_state.login_admin = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.menu = "🏠 Beranda"
            st.rerun()

    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            data_admin = check_login(username, password)

            if data_admin is not None:
                st.session_state.login_admin = True
                st.session_state.username = data_admin["username"]
                st.session_state.role = data_admin["role"]
                if data_admin["role"] == "pakar":
                    st.session_state.menu = "⚙️ Admin Panel"
                else:
                    st.session_state.menu = "🔍 Diagnosa"

                st.rerun()
            else:
                st.error("Username atau password salah.")
# =========================
# ADMIN PANEL
# =========================
elif menu == "⚙️ Admin Panel":
    st.title("⚙️ Admin Panel")
    if not st.session_state.get("login_admin", False):
        st.warning("Silakan login terlebih dahulu.")
        st.stop()

    if st.session_state.get("role") != "pakar":
        st.error("Akses ditolak. Admin Panel hanya untuk pakar.")
        st.stop()

    else:
        st.success("Anda masuk sebagai admin.")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Dataset",
            "➕ Tambah Dataset",
            "🌿 Kelola Penyakit",
            "🩺 Kelola Gejala",
            "👤 Kelola Admin"
        ])
        # =========================
        # TAB DATASET
        # =========================
        with tab1:
                st.subheader("📊 Data Training")

                dataset_df = get_dataset()
                penyakit_df = get_penyakit()
                gejala_df = get_gejala()

                kolom_gejala_aktif = gejala_df["kode_gejala"].tolist()
                kode_penyakit_aktif = penyakit_df["kode_penyakit"].tolist()

                dataset_df = dataset_df[
                    kolom_gejala_aktif + ["penyakit"]
                ]

                dataset_df = dataset_df[
                    dataset_df["penyakit"].isin(kode_penyakit_aktif)
                ]

                # =========================
                # FILTER PENYAKIT
                # =========================
                pilihan_filter = st.selectbox(
                    "Filter Penyakit",
                    ["Semua"] + penyakit_df["kode_penyakit"].tolist()
                )

                if pilihan_filter == "Semua":
                    dataset_tampil = dataset_df
                else:
                    dataset_tampil = dataset_df[
                        dataset_df["penyakit"] == pilihan_filter
                    ]

                dataset_df = get_dataset_with_id()

                # tetap filter gejala dan penyakit aktif
                kolom_gejala_aktif = gejala_df["kode_gejala"].tolist()
                kode_penyakit_aktif = penyakit_df["kode_penyakit"].tolist()

                dataset_df = dataset_df[
                    ["id"] + kolom_gejala_aktif + ["penyakit"]
                ]

                dataset_df = dataset_df[
                    dataset_df["penyakit"].isin(kode_penyakit_aktif)
                ]

                if pilihan_filter == "Semua":
                    dataset_tampil = dataset_df.copy()
                else:
                    dataset_tampil = dataset_df[
                        dataset_df["penyakit"] == pilihan_filter
                    ].copy()

                dataset_tampil.insert(0, "pilih", False)

                edited_df = st.data_editor(
                    dataset_tampil,
                    disabled=[
                        col for col in dataset_tampil.columns
                        if col != "pilih"
                    ],
                    hide_index=True,
                    use_container_width=True
                )

                data_dipilih = edited_df[edited_df["pilih"] == True]

                if not data_dipilih.empty:
                    st.warning(f"{len(data_dipilih)} data dipilih untuk dihapus.")

                    if st.button("🗑️ Hapus Dataset Terpilih"):
                        st.session_state.dataset_hapus_ids = data_dipilih["id"].tolist()
                        st.rerun()

                # =========================
                # STATISTIK
                # =========================
                gejala_df = get_gejala()

                st.write(f"Jumlah data: **{len(dataset_tampil)}**")
                st.write(f"Jumlah gejala: **{len(gejala_df)}**")
                st.write(f"Jumlah penyakit: **{dataset_df['penyakit'].nunique()}**")

                st.subheader("📌 Jumlah Data Per Penyakit")

                jumlah_penyakit = (
                    dataset_df["penyakit"]
                    .value_counts()
                    .reset_index()
                )

                jumlah_penyakit.columns = ["kode_penyakit", "jumlah_data"]

                jumlah_penyakit = jumlah_penyakit.merge(
                    penyakit_df[["kode_penyakit", "nama_penyakit"]],
                    on="kode_penyakit",
                    how="left"
                )

                jumlah_penyakit = jumlah_penyakit[
                    ["kode_penyakit", "nama_penyakit", "jumlah_data"]
                ]

                st.dataframe(jumlah_penyakit)

        # =========================
        # TAB TAMBAH DATASET
        # =========================
        with tab2:

            st.subheader("➕ Tambah Data Training")

            # =========================
            # TAB INPUT MANUAL
            # =========================
            tab_manual, tab_csv = st.tabs([
                "🖊️ Input Manual",
                "📂 Upload CSV"
            ])

            # =========================
            # INPUT MANUAL
            # =========================
            with tab_manual:

                gejala_penyakit = []

                gejala_df = get_gejala()

                cols = st.columns(2)

                for i, row in gejala_df.iterrows():

                    kode = row["kode_gejala"]
                    nama = row["nama_gejala"]

                    with cols[i % 2]:

                        pilih = st.checkbox(
                            f"{kode} - {nama}",
                            key=f"dataset_{kode}"
                        )

                        gejala_penyakit.append(1 if pilih else 0)

                penyakit_df = get_penyakit()

                pilihan_penyakit = st.selectbox(
                    "Pilih Penyakit",
                    penyakit_df["nama_penyakit"].tolist()
                )

                kode_penyakit = penyakit_df[
                    penyakit_df["nama_penyakit"] == pilihan_penyakit
                ]["kode_penyakit"].iloc[0]

                if st.button("💾 Simpan Dataset"):

                    tambah_dataset(
                        gejala_penyakit,
                        kode_penyakit
                    )

                    st.cache_data.clear()
                    st.cache_resource.clear()

                    st.success("Data training berhasil ditambahkan.")

                    st.rerun()

            # =========================
            # UPLOAD CSV
            # =========================
            with tab_csv:

                st.info("""
                Format CSV harus:
                - G1 sampai G24 atau dan seterusnya, dengan isi 1 atau 0
                - kolom terakhir = penyakit, dengan isi kode penyakit yaitu P1 sampai P8 atau dan seterusnya
                """)

                file_dataset = st.file_uploader(
                    "Upload Dataset CSV",
                    type=["csv"]
                )

                if file_dataset is not None:

                    preview = pd.read_csv(
                        file_dataset,
                        sep=";"
                    )

                    st.write("Preview Dataset")

                    st.dataframe(preview)

                    if st.button("📥 Import Dataset CSV"):

                        file_dataset.seek(0)

                        tambah_dataset_csv(file_dataset)

                        st.cache_data.clear()
                        st.cache_resource.clear()

                        st.success("Dataset berhasil diimport.")

                        st.rerun()
        # =========================
        # TAB TAMBAH PENYAKIT
        # =========================
        with tab3:
            st.subheader("🌿 Kelola Penyakit")

            penyakit_df = get_penyakit()

            pilihan = st.selectbox(
                "Pilih Penyakit",
                ["Tambah Penyakit Baru"] +
                (
                    penyakit_df["kode_penyakit"] +
                    " - " +
                    penyakit_df["nama_penyakit"]
                ).tolist()
            )

            # =========================
            # MODE TAMBAH
            # =========================
            if pilihan == "Tambah Penyakit Baru":
                kode_penyakit = st.text_input("Kode Penyakit")
                nama_penyakit = st.text_input("Nama Penyakit")
                deskripsi = st.text_area("Deskripsi")
                penanganan = st.text_area("Penanganan")

                if st.button("💾 Simpan Penyakit"):
                    if (
                        kode_penyakit == ""
                        or nama_penyakit == ""
                        or deskripsi == ""
                        or penanganan == ""
                    ):
                        st.warning("Semua field wajib diisi.")

                    else:
                        hasil = tambah_penyakit(
                            kode_penyakit,
                            nama_penyakit,
                            deskripsi,
                            penanganan
                        )

                        if hasil == True:
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            st.success(f"Penyakit '{kode_penyakit}' berhasil ditambahkan.")
                            st.rerun()

                        elif hasil == "FORMAT_SALAH":
                            st.warning("Format kode penyakit harus seperti P1, P2, P25.")

                        else:
                            st.warning(f"Kode penyakit '{hasil}' sudah ada.")

            # =========================
            # MODE EDIT
            # =========================
            else:
                kode = pilihan.split(" - ")[0]
                data_pilih = penyakit_df[
                    penyakit_df["kode_penyakit"] == kode
                ].iloc[0]
                kode_penyakit = st.text_input(
                    "Kode Penyakit",
                    value=data_pilih["kode_penyakit"]
                )
                nama_penyakit = st.text_input(
                    "Nama Penyakit",
                    value=data_pilih["nama_penyakit"]
                )
                deskripsi = st.text_area(
                    "Deskripsi",
                    value=data_pilih["deskripsi"]
                )
                penanganan = st.text_area(
                    "Penanganan",
                    value=data_pilih["penanganan"]
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Update Penyakit"):
                        edit_penyakit(
                            data_pilih["kode_penyakit"],
                            kode_penyakit,
                            nama_penyakit,
                            deskripsi,
                            penanganan
                        )

                        st.cache_data.clear()
                        st.cache_resource.clear()

                        st.success("Penyakit berhasil diperbarui.")
                        st.rerun()

                with col2:
                    if st.button("🚫 Nonaktifkan Penyakit"):
                        nonaktifkan_penyakit(data_pilih["kode_penyakit"])

                        st.cache_data.clear()
                        st.cache_resource.clear()

                        st.success("Penyakit berhasil dinonaktifkan.")
                        st.rerun()
        # =========================
        # TAB TAMBAH GEJALA
        # =========================
        with tab4:

            st.subheader("🩺 Kelola Gejala")
            if "pesan_gejala" in st.session_state:
                st.success(st.session_state.pesan_gejala)
                del st.session_state.pesan_gejala
            gejala_df = get_gejala()

            pilihan_gejala = st.selectbox(
                "Pilih Gejala",
                ["Tambah Gejala Baru"] +
                (
                    gejala_df["kode_gejala"] +
                    " - " +
                    gejala_df["nama_gejala"]
                ).tolist()
            )

            # =========================
            # MODE TAMBAH
            # =========================
            if pilihan_gejala == "Tambah Gejala Baru":
                kode_gejala = st.text_input(
                "Kode Gejala",
                placeholder="Contoh: G26"
                )
                nama_gejala = st.text_input(
                    "Nama Gejala",
                    placeholder="Contoh: Daun menguning"
                )
                if st.button("Simpan Gejala"):

                    if kode_gejala == "" or nama_gejala == "":
                        st.warning("Semua field wajib diisi.")
                    else:
                        hasil = tambah_gejala(
                            kode_gejala,
                            nama_gejala
                        )
                        if hasil == True:
                            st.cache_data.clear()
                            st.cache_resource.clear()
                            st.session_state.pesan_gejala = f"Gejala '{kode_gejala}' berhasil ditambahkan."
                            st.rerun()
                        elif hasil == "FORMAT_SALAH":
                            st.warning(
                                "Format kode gejala harus seperti G1, G2, G25."
                            )
                        else:
                            st.warning(
                                f"Kode gejala '{hasil}' sudah ada."
                            )

            # =========================
            # MODE EDIT
            # =========================
            else:
                kode = pilihan_gejala.split(" - ")[0]
                data_gejala = gejala_df[
                    gejala_df["kode_gejala"] == kode
                ].iloc[0]
                id_gejala = int(data_gejala["id"])
                st.text_input(
                    "Kode Gejala",
                    value=data_gejala["kode_gejala"],
                    disabled=True
                )
                nama_gejala = st.text_input(
                    "Nama Gejala",
                    value=data_gejala["nama_gejala"]
                )
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Update Gejala"):
                        edit_gejala(
                            id_gejala,
                            nama_gejala
                        )

                        st.cache_data.clear()
                        st.cache_resource.clear()

                        st.session_state.pesan_gejala = f"Gejala '{data_gejala['kode_gejala']}' berhasil diupdate."
                        st.rerun()

                with col2:
                    if st.button("🚫 Nonaktifkan Gejala"):
                        nonaktifkan_gejala(id_gejala)

                        st.cache_data.clear()
                        st.cache_resource.clear()

                        st.session_state.pesan_gejala = f"Gejala '{data_gejala['kode_gejala']}' berhasil dinonaktifkan."
                        st.rerun()
        # =========================
        # TAB TAMBAH ADMIN
        # =========================
        with tab5:
            st.subheader("👤 Kelola Admin")

            admin_df = get_admin()

            st.write("### 📋 Daftar Akun")
            st.dataframe(
                admin_df,
                use_container_width=True
            )

            st.divider()

            st.write("### ➕ Tambah Akun")

            username_baru = st.text_input("Username Baru")
            password_baru = st.text_input("Password Baru", type="password")

            role_baru = st.selectbox(
                "Role Akun",
                ["pakar", "staff"]
            )

            if st.button("💾 Simpan Akun"):
                if username_baru == "" or password_baru == "":
                    st.warning("Username dan password wajib diisi.")
                else:
                    tambah_admin(
                        username_baru,
                        password_baru,
                        role_baru
                    )

                    st.cache_data.clear()
                    st.success("Akun berhasil ditambahkan.")
                    st.rerun()
# =========================
# RIWAYAT DIAGNOSA
# =========================

elif menu == "📋 Riwayat Diagnosa":

    st.title("📋 Riwayat Diagnosa")

    riwayat_df = get_riwayat_diagnosa()

    if riwayat_df.empty:
        st.info("Belum ada riwayat diagnosa.")
    else:
        st.subheader("📊 Tabel Riwayat")
        header = st.columns([1, 2, 2, 1, 3,1, 1, 1])

        header[0].markdown("**ID**")
        header[1].markdown("**Tanggal**")
        header[2].markdown("**Username**")
        header[3].markdown("**Role**")
        header[4].markdown("**Hasil Penyakit**")
        header[5].markdown("**Keyakinan**")
        header[6].markdown("**Status**")
        header[7].markdown("**Action**")

        st.markdown("""
        <hr style="margin-top:5px; margin-bottom:10px;">
        """, unsafe_allow_html=True)

        for _, row in riwayat_df.iterrows():

            with st.container(border=True):

                col = st.columns([1, 2, 2, 1, 3, 1,1, 1])

                col[0].write(row["id"])
                col[1].write(row["tanggal"])
                col[2].write(row["username"])
                col[3].write(row["role"])
                col[4].write(row["hasil_penyakit"])
                nilai = row["nilai_keanggotaan"]
                persen = nilai * 100 if pd.notna(nilai) else 0

                col[5].write(f"{persen:.2f}%")
                status = row["status"]

                if status == "diterima":
                    warna_bg = "#2e7d32"
                    warna_text = "white"

                elif status == "ditolak":
                    warna_bg = "#c62828"
                    warna_text = "white"

                else:
                    warna_bg = "#b28704"
                    warna_text = "white"

                col[6].markdown(
                    f"""
                    <div style="
                        background-color:{warna_bg};
                        color:{warna_text};
                        padding:6px;
                        border-radius:10px;
                        text-align:center;
                        font-weight:600;
                        font-size:14px;
                    ">
                        {status.upper()}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                with col[7]:
                    if st.button(
                        "🔍 Detail",
                        key=f"detail_{row['id']}"
                    ):
                        st.session_state.id_detail_riwayat = int(row["id"])
                        detail_riwayat_dialog()

# =========================
# RIWAYAT SAYA
# =========================                       
elif menu == "📋 Riwayat Saya":

    st.title("📋 Riwayat Saya")

    username = st.session_state.get("username")

    riwayat_df = get_riwayat_saya(username)

    if riwayat_df.empty:

        st.info("Belum ada riwayat diagnosa.")

    else:

        header = st.columns([1, 2, 3, 2, 1])

        header[0].markdown("**ID**")
        header[1].markdown("**Tanggal**")
        header[2].markdown("**Hasil Penyakit**")
        header[3].markdown("**Status**")
        header[4].markdown("**Action**")

        st.markdown("""
        <hr style="margin-top:5px; margin-bottom:10px;">
        """, unsafe_allow_html=True)

        for _, row in riwayat_df.iterrows():

            with st.container(border=True):

                col = st.columns([1, 2, 3, 2, 1])

                col[0].write(row["id"])
                col[1].write(row["tanggal"])
                col[2].write(row["hasil_penyakit"])
                status = row["status"]

                if status == "diterima":
                    warna_bg = "#2e7d32"
                    warna_text = "white"

                elif status == "ditolak":
                    warna_bg = "#c62828"
                    warna_text = "white"

                else:
                    warna_bg = "#b28704"
                    warna_text = "white"

                col[3].markdown(
                    f"""
                    <div style="
                        background-color:{warna_bg};
                        color:{warna_text};
                        padding:6px;
                        border-radius:10px;
                        text-align:center;
                        font-weight:600;
                        font-size:14px;
                    ">
                        {status.upper()}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                with col[4]:

                    if st.button(
                        "🔍",
                        key=f"detail_saya_{row['id']}"
                    ):

                        st.session_state.id_detail_riwayat = int(row["id"])

                        detail_riwayat_staff()