import os

from database import (
    create_tables,
    import_gejala_csv,
    import_penyakit_csv,
    import_dataset_csv
)

DB_NAME = "edamame.db"

# hapus database lama
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

# buat tabel
create_tables()

# import semua csv
import_gejala_csv("gejala.csv")
import_penyakit_csv("penyakit.csv")
import_dataset_csv("dataset_edamame.csv")

print("Database berhasil dibuat.")