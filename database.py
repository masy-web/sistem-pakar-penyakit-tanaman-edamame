import sqlite3
import pandas as pd
import re
from datetime import datetime
import json
DB_NAME = "edamame.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'staff'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gejala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_gejala TEXT UNIQUE,
        nama_gejala TEXT,
        aktif INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS penyakit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kode_penyakit TEXT UNIQUE,
        nama_penyakit TEXT UNIQUE,
        deskripsi TEXT,
        penanganan TEXT,
        aktif INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dataset (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        penyakit TEXT
    )
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO admin (username, password, role)
    VALUES ('admin', 'admin123', 'pakar'),
    ('user','user1','staff')
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS riwayat_diagnosa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT,
        username TEXT,
        role TEXT,
        data_gejala TEXT,
        gejala_dipilih TEXT,
        hasil_kode TEXT,
        hasil_penyakit TEXT,
        nilai_keanggotaan REAL,
        status TEXT DEFAULT 'menunggu'
    )
    """)
    
    conn.commit()
    conn.close()
    
    # Database

def import_dataset_csv(csv_file):
    conn = get_connection()
    df = pd.read_csv(csv_file, sep=";")
    # 
    # HAPUS LABEL KOSONG
    
    df = df.dropna(subset=["penyakit"])
    
    # AMBIL SEMUA KOLOM GEJALA
    
    kolom_gejala = [
        col for col in df.columns
        if col.startswith("G")
    ]
    
    # VALIDASI NILAI GEJALA 
    for col in kolom_gejala:
        # ubah selain 0/1 menjadi 0
        df[col] = df[col].apply(
            lambda x: 1 if x == 1 else 0
        )

    # VALIDASI PENYAKIT

    penyakit_df = pd.read_sql_query(
        "SELECT kode_penyakit FROM penyakit",
        conn
    )
    kode_valid = penyakit_df[
        "kode_penyakit"
    ].tolist()
    # hanya ambil penyakit yang valid
    df = df[
        df["penyakit"].isin(kode_valid)
    ]
    # 
    # SIMPAN
    # 
    df.to_sql(
        "dataset",
        conn,
        if_exists="replace",
        index=False
    )
    conn.close()
    print("Dataset berhasil diimport.")
    
def get_dataset():
    conn = get_connection()

    df = pd.read_sql_query("SELECT * FROM dataset", conn)

    conn.close()

    if "id" in df.columns:
        df = df.drop(columns=["id"])

    if "penyakit" in df.columns:
        kolom_gejala = [
            col for col in df.columns
            if col != "penyakit"
        ]

        df = df[kolom_gejala + ["penyakit"]]

    return df
def get_dataset_with_id():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT rowid AS id, * FROM dataset",
        conn
    )

    conn.close()
    return df


def hapus_dataset_by_ids(id_list):
    conn = get_connection()
    cursor = conn.cursor()

    for id_dataset in id_list:
        cursor.execute(
            "DELETE FROM dataset WHERE rowid=?",
            (int(id_dataset),)
        )

    conn.commit()
    conn.close()

def tambah_dataset(data_gejala, penyakit):
    conn = get_connection()
    cursor = conn.cursor()
    gejala_df = get_gejala()
    kolom_gejala = gejala_df["kode_gejala"].tolist()
    kolom = ", ".join(kolom_gejala) + ", penyakit"
    placeholder = ", ".join(["?"] * (len(kolom_gejala) + 1))
    cursor.execute(
        f"INSERT INTO dataset ({kolom}) VALUES ({placeholder})",
        data_gejala + [penyakit]
    )
    conn.commit()
    conn.close()
    
def tambah_dataset_csv(uploaded_file):
    conn = get_connection()

    df = pd.read_csv(uploaded_file, sep=";")

    df.to_sql(
        "dataset",
        conn,
        if_exists="append",
        index=False
    )
    conn.close() 
   


def simpan_riwayat_diagnosa(username, role, data_gejala, gejala_dipilih, hasil_kode, hasil_penyakit,nilai_keanggotaan, status="menunggu"):
    conn = get_connection()
    cursor = conn.cursor()

    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO riwayat_diagnosa
        (tanggal, username, role, data_gejala, gejala_dipilih, hasil_kode, hasil_penyakit, nilai_keanggotaan, status)
        VALUES (?, ?, ?, ?, ?, ?, ?,?,?)
    """, (
        tanggal,
        username,
        role,
        json.dumps(data_gejala),
        ", ".join(gejala_dipilih),
        hasil_kode,
        hasil_penyakit,
        nilai_keanggotaan,
        status
    ))

    conn.commit()
    conn.close()

def get_riwayat_diagnosa():
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            tanggal,
            username,
            role,
            hasil_penyakit,
            nilai_keanggotaan,
            status
        FROM riwayat_diagnosa
        ORDER BY id DESC
    """, conn)

    conn.close()

    return df

def get_riwayat_saya(username):

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            id,
            tanggal,
            hasil_penyakit,
            status
        FROM riwayat_diagnosa
        WHERE username=?
        ORDER BY id DESC
        """,
        conn,
        params=(username,)
    )

    conn.close()
    return df

def get_detail_riwayat(id_riwayat):
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM riwayat_diagnosa
        WHERE id=?
        """,
        conn,
        params=(id_riwayat,)
    )

    conn.close()

    if df.empty:
        return None

    return df.iloc[0]  

def validasi_riwayat(id_riwayat):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT data_gejala, hasil_kode
        FROM riwayat_diagnosa
        WHERE id=?
        """,
        (id_riwayat,)
    )

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return False

    data_gejala_json, hasil_kode = result

    data_gejala = json.loads(data_gejala_json)

    gejala_df = get_gejala()

    kolom_gejala = gejala_df["kode_gejala"].tolist()
    if len(data_gejala) < len(kolom_gejala):
        data_gejala = data_gejala + [0] * (len(kolom_gejala) - len(data_gejala))

    elif len(data_gejala) > len(kolom_gejala):
        data_gejala = data_gejala[:len(kolom_gejala)]
    kolom = ", ".join(kolom_gejala) + ", penyakit"

    placeholder = ", ".join(
        ["?"] * (len(kolom_gejala) + 1)
    )

    cursor.execute(
        f"""
        INSERT INTO dataset ({kolom})
        VALUES ({placeholder})
        """,
        data_gejala + [hasil_kode]
    )

    cursor.execute(
        """
        UPDATE riwayat_diagnosa
        SET status='diterima'
        WHERE id=?
        """,
        (id_riwayat,)
    )

    conn.commit()
    conn.close()

    return True
def tolak_riwayat(id_riwayat):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE riwayat_diagnosa
        SET status='ditolak'
        WHERE id=?
        """,
        (id_riwayat,)
    )

    conn.commit()
    conn.close()
      
    # Admin
def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, role
        FROM admin
        WHERE username=? AND password=?
        """,
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return None

    return {
        "id": result[0],
        "username": result[1],
        "role": result[2]
    }


def get_admin():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT id, username, role FROM admin",
        conn
    )

    conn.close()
    return df


def tambah_admin(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO admin (username, password, role)
        VALUES (?, ?, ?)
        """,
        (username, password, role)
    )

    conn.commit()
    conn.close()


def ubah_password_admin(username, password_lama, password_baru):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM admin WHERE username=? AND password=?",
        (username, password_lama)
    )

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return False

    cursor.execute(
        "UPDATE admin SET password=? WHERE username=?",
        (password_baru, username)
    )

    conn.commit()
    conn.close()

    return True
    
    # Gejala
def import_gejala_csv(csv_file):
    conn = get_connection()
    cursor = conn.cursor()
    df = pd.read_csv(csv_file, sep=";")
    for _, row in df.iterrows():
        kode = row["kode_gejala"]
        nama = row["nama_gejala"]
        cursor.execute(
            """
            INSERT OR IGNORE INTO gejala (kode_gejala, nama_gejala, aktif)
            VALUES (?, ?, 1)
            """,
            (kode, nama)
        )
        cursor.execute("PRAGMA table_info(dataset)")
        kolom_dataset = [kolom[1] for kolom in cursor.fetchall()]
        if kode not in kolom_dataset:
            cursor.execute(
                f"ALTER TABLE dataset ADD COLUMN {kode} INTEGER DEFAULT 0"
            )
    conn.commit()
    conn.close()   
     
def tambah_gejala(kode_gejala, nama_gejala):
    conn = get_connection()
    cursor = conn.cursor()

    kode_gejala = kode_gejala.strip().upper()
    nama_gejala = nama_gejala.strip()
     # =========================
    # VALIDASI FORMAT
    # =========================
    if not re.fullmatch(r"G\d+", kode_gejala):
        conn.close()
        return "FORMAT_SALAH"

    # cek apakah kode sudah ada
    cursor.execute(
        "SELECT id FROM gejala WHERE kode_gejala=?",
        (kode_gejala,)
    )

    result = cursor.fetchone()

    if result is not None:
        conn.close()
        return kode_gejala

    # simpan ke tabel gejala
    cursor.execute(
        """
        INSERT INTO gejala (kode_gejala, nama_gejala, aktif)
        VALUES (?, ?, 1)
        """,
        (kode_gejala, nama_gejala)
    )

    # cek kolom dataset
    cursor.execute("PRAGMA table_info(dataset)")
    kolom_dataset = [kolom[1] for kolom in cursor.fetchall()]

    # tambah kolom dataset jika belum ada
    if kode_gejala not in kolom_dataset:
        cursor.execute(
            f"ALTER TABLE dataset ADD COLUMN {kode_gejala} INTEGER DEFAULT 0"
        )

    conn.commit()
    conn.close()

    return True

def get_gejala():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM gejala WHERE aktif=1",
        conn
    )
    conn.close()
    return df

def edit_gejala(id_gejala, nama_gejala):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE gejala SET nama_gejala=? WHERE id=?",
        (nama_gejala, id_gejala)
    )
    conn.commit()
    conn.close()
def nonaktifkan_gejala(id_gejala):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE gejala SET aktif=0 WHERE id=?",
        (id_gejala,)
    )

    conn.commit()
    conn.close()
        
# Penyakit
def import_penyakit_csv(csv_file):
    conn = get_connection()
    df = pd.read_csv(csv_file, sep=";")
    df["aktif"] = 1
    df.to_sql(
        "penyakit",
        conn,
        if_exists="replace",
        index=False
    )
    conn.close()

def get_penyakit():
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT 
            rowid AS id,
            kode_penyakit,
            nama_penyakit,
            deskripsi,
            penanganan,
            aktif
        FROM penyakit
        WHERE aktif=1
        """,
        conn
    )

    conn.close()
    return df

def tambah_penyakit(kode_penyakit, nama_penyakit, deskripsi, penanganan):
    conn = get_connection()
    cursor = conn.cursor()

    kode_penyakit = kode_penyakit.strip().upper()
    nama_penyakit = nama_penyakit.strip()
    deskripsi = deskripsi.strip()
    penanganan = penanganan.strip()

    # =========================
    # VALIDASI FORMAT
    # =========================
    if not re.fullmatch(r"P\d+", kode_penyakit):
        conn.close()
        return "FORMAT_SALAH"

    # cek apakah kode penyakit sudah ada
    cursor.execute(
        "SELECT kode_penyakit FROM penyakit WHERE kode_penyakit=?",
        (kode_penyakit,)
    )

    result = cursor.fetchone()

    if result is not None:
        conn.close()
        return kode_penyakit

    # simpan ke tabel penyakit
    cursor.execute(
        """
        INSERT INTO penyakit 
        (kode_penyakit, nama_penyakit, deskripsi, penanganan, aktif)
        VALUES (?, ?, ?, ?, 1)
        """,
        (
            kode_penyakit,
            nama_penyakit,
            deskripsi,
            penanganan
        )
    )

    conn.commit()
    conn.close()

    return True

def edit_penyakit(kode_lama,kode_penyakit,
    nama_penyakit,deskripsi,penanganan
    ):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE penyakit
        SET
            kode_penyakit=?,
            nama_penyakit=?,
            deskripsi=?,
            penanganan=?
        WHERE kode_penyakit=?
        """,
        (
            kode_penyakit,
            nama_penyakit,
            deskripsi,
            penanganan,
            kode_lama
        )
    )
    conn.commit()
    conn.close()
def nonaktifkan_penyakit(kode_penyakit):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE penyakit SET aktif=0 WHERE kode_penyakit=?",
        (kode_penyakit,)
    )

    conn.commit()
    conn.close()