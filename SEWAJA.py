import os
import pandas as pd

FILE_USERS = "users.csv"
FILE_KATALOG = "katalog.csv"
FILE_TRANSAKSI = "transaksi.csv"

def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")

def jeda():
    try:
        input("\nTekan Enter untuk melanjutkan...")
    except (EOFError, KeyboardInterrupt):
        pass

def inisialisasi_berkas():
    """Membuat file CSV dasar jika belum tersedia agar terhindar dari FileNotFoundError."""
    if not os.path.exists(FILE_USERS):
        pd.DataFrame([
            {"username": "admin", "password": "Admin@123", "role": "admin", "nama": "Administrator"}
        ]).to_csv(FILE_USERS, index=False)

    if not os.path.exists(FILE_KATALOG):
        pd.DataFrame(columns=[
            "id_barang", "nama_barang", "kategori", "harga_per_hari", "stok"
        ]).to_csv(FILE_KATALOG, index=False)

    if not os.path.exists(FILE_TRANSAKSI):
        pd.DataFrame(columns=[
            "id_transaksi", "username", "nama_barang", "durasi_hari", "total_biaya", "status"
        ]).to_csv(FILE_TRANSAKSI, index=False)

# ==========================================================
# HELPER TABEL & VALIDASI INPUT
# ==========================================================

def cetak_tabel(df, kolom_rupiah=None):
    """Mencetak DataFrame menjadi tabel berbingkai garis rapi di terminal."""
    if df.empty:
        print("+------------------------------------------+")
        print("|          Data masih kosong.              |")
        print("+------------------------------------------+")
        return

    df_tampil = df.copy()

    # Konversi aman untuk kolom bilangan bulat agar tidak crash (ValueError)
    for col_int in ["id_barang", "stok", "durasi_hari", "id_transaksi", "no"]:
        if col_int in df_tampil.columns:
            df_tampil[col_int] = pd.to_numeric(df_tampil[col_int], errors="coerce").fillna(0).astype(int)

    if kolom_rupiah:
        for kolom in kolom_rupiah:
            if kolom in df_tampil.columns:
                nilai_num = pd.to_numeric(df_tampil[kolom], errors="coerce").fillna(0).astype(int)
                df_tampil[kolom] = nilai_num.apply(lambda x: f"Rp {x:,}")

    df_tampil = df_tampil.fillna("-")

    lebar = {
        col: max(len(str(col)), df_tampil[col].apply(lambda x: len(str(x))).max()) + 2
        for col in df_tampil.columns
    }
    garis = "+" + "+".join("-" * lebar[col] for col in df_tampil.columns) + "+"

    print(garis)
    print("|" + "|".join(f" {str(col).ljust(lebar[col] - 1)}" for col in df_tampil.columns) + "|")
    print(garis)
    for _, row in df_tampil.iterrows():
        print("|" + "|".join(f" {str(row[col]).ljust(lebar[col] - 1)}" for col in df_tampil.columns) + "|")
    print(garis)

def password_valid(pw):
    if len(pw) < 8:
        return False
    return (
        any(c.isupper() for c in pw)
        and any(c.islower() for c in pw)
        and any(c.isdigit() for c in pw)
        and any(not c.isalnum() and not c.isspace() for c in pw)
    )

def input_teks(pesan, daftar_duplikat=None, lower=False):
    while True:
        val = input(pesan).strip()
        if val == "0":
            return None
        if not val:
            print("Input tidak boleh kosong!")
            continue
        cek = val.lower()
        if daftar_duplikat is not None and cek in [str(x).lower() for x in daftar_duplikat]:
            print(f"'{val}' sudah terdaftar! Gunakan data lain.")
            continue
        return cek if lower else val

def input_angka(pesan, minimal=1, daftar_duplikat=None):
    while True:
        val = input(pesan).strip()
        if val == "0":
            return None
        try:
            angka = int(val)
            if angka < minimal:
                print(f"Nilai minimal adalah {minimal}!")
                continue
            if daftar_duplikat is not None and angka in [int(x) for x in daftar_duplikat]:
                print(f"ID '{angka}' sudah digunakan! Gunakan ID lain.")
                continue
            return angka
        except ValueError:
            print("Format salah! Harus berupa angka.")

# ==========================================================
# 1. AUTENTIKASI (REGISTRASI & LOGIN)
# ==========================================================

def registrasi_customer():
    bersihkan_layar()
    print("=== REGISTRASI CUSTOMER === (Ketik '0' untuk kembali)\n")
    df_users = pd.read_csv(FILE_USERS)

    nama = input_teks("Nama Lengkap : ")
    if nama is None:
        return

    username = input_teks("Username     : ", daftar_duplikat=df_users["username"].values, lower=True)
    if username is None:
        return

    print("Password min. 8 karakter (Kapital, Kecil, Angka, Simbol)")
    while True:
        password = input("Password     : ").strip()
        if password == "0":
            return
        if not password_valid(password):
            print("Password tidak memenuhi syarat! Ulangi.")
            continue
        break

    baru = pd.DataFrame([{"username": username, "password": password, "role": "customer", "nama": nama}])
    pd.concat([df_users, baru], ignore_index=True).to_csv(FILE_USERS, index=False)
    print(f"\nRegistrasi berhasil! Akun '{username}' dibuat.")
    jeda()

def login():
    bersihkan_layar()
    print("=== LOGIN SEWAJA === (Ketik '0' untuk kembali)\n")
    df_users = pd.read_csv(FILE_USERS)

    while True:
        username = input("Username : ").strip().lower()
        if username == "0":
            return None, None
        user = df_users[df_users["username"].astype(str).str.lower() == username]
        if user.empty:
            print("Username tidak ditemukan!\n")
            continue

        while True:
            password = input("Password : ").strip()
            if password == "0":
                return None, None
            if str(user.iloc[0]["password"]) != password:
                print("Password salah! Masukkan password kembali.\n")
                continue
            print(f"\nLogin berhasil! Selamat datang, {user.iloc[0]['nama']}.")
            jeda()
            return username, str(user.iloc[0]["role"]).strip().lower()

# ==========================================================
# 2. FITUR CUSTOMER
# ==========================================================

def lihat_katalog():
    df = pd.read_csv(FILE_KATALOG)
    print("\n--- DAFTAR KATALOG UNIT SEWA ---")
    cetak_tabel(df, kolom_rupiah=["harga_per_hari"])

def tampilkan_tabel_keranjang(keranjang):
    print("\n--- ISI KERANJANG SEWA SAYA ---")
    if not keranjang:
        print("+------------------------------------------+")
        print("|        Keranjang masih kosong.           |")
        print("+------------------------------------------+")
        return False

    df_k = pd.DataFrame(keranjang)
    df_k.insert(0, "no", range(1, len(df_k) + 1))
    cetak_tabel(df_k, kolom_rupiah=["harga_per_hari", "subtotal"])
    print(f"TOTAL ESTIMASI BIAYA : Rp {int(df_k['subtotal'].sum()):,}")
    return True

def cari_katalog():
    while True:
        bersihkan_layar()
        print("=== CARI UNIT KATALOG ===")
        lihat_katalog()
        key = input("\nCari nama/kategori (iPhone/Kamera) atau '0' kembali: ").strip().lower()
        if key == "0":
            return

        df = pd.read_csv(FILE_KATALOG)
        hasil = df[
            df["nama_barang"].astype(str).str.lower().str.contains(key, na=False)
            | df["kategori"].astype(str).str.lower().str.contains(key, na=False)
        ]
        print("\n--- HASIL PENCARIAN ---")
        if hasil.empty:
            print("Barang tidak ditemukan.")
        else:
            cetak_tabel(hasil, kolom_rupiah=["harga_per_hari"])

        if input("\nCari lagi? (y/n): ").strip().lower() != "y":
            break

def edit_profil(username_login):
    bersihkan_layar()
    print("=== EDIT PROFIL AKUN === (Ketik '0' untuk kembali)\n")
    df_users = pd.read_csv(FILE_USERS)
    match = df_users[df_users["username"].astype(str).str.lower() == username_login]

    if match.empty:
        print("Data akun tidak ditemukan!")
        jeda()
        return

    idx = match.index[0]

    print(f"Username          : {df_users.loc[idx, 'username']}")
    print(f"Nama Saat Ini     : {df_users.loc[idx, 'nama']}")
    print(f"Password Saat Ini : {df_users.loc[idx, 'password']}\n")

    nama_baru = input("Nama baru (kosongkan jika tetap)     : ").strip()
    if nama_baru == "0":
        return

    while True:
        pass_baru = input("Password baru (kosongkan jika tetap) : ").strip()
        if pass_baru == "0":
            return
        if pass_baru and not password_valid(pass_baru):
            print("Password minimal 8 karakter (Kapital, Kecil, Angka, Simbol)!")
            continue
        break

    if nama_baru:
        df_users.loc[idx, "nama"] = nama_baru
    if pass_baru:
        df_users.loc[idx, "password"] = pass_baru
    df_users.to_csv(FILE_USERS, index=False)
    print("\nProfil berhasil diperbarui.")
    jeda()

def keranjang_sewa(username_login):
    keranjang = []
    while True:
        bersihkan_layar()
        print("=== KERANJANG & SEWA UNIT ===")
        lihat_katalog()
        tampilkan_tabel_keranjang(keranjang)

        print("\nMenu Keranjang:")
        print("1. Lihat daftar katalog produk")
        print("2. Tambah unit ke keranjang")
        print("3. Ubah durasi sewa")
        print("4. Hapus unit dari keranjang")
        print("5. Checkout & Konfirmasi sewa")
        print("0. Kembali ke menu customer")
        pilih = input("\nPilih menu: ").strip()

        if pilih == "1":
            bersihkan_layar()
            lihat_katalog()
            jeda()

        elif pilih == "2":
            bersihkan_layar()
            print("=== TAMBAH UNIT KE KERANJANG ===")
            lihat_katalog()
            tampilkan_tabel_keranjang(keranjang)

            df_kat = pd.read_csv(FILE_KATALOG)
            if df_kat.empty:
                print("\nKatalog masih kosong.")
                jeda()
                continue

            while True:
                id_b = input_angka("\nMasukkan ID Barang (atau '0' kembali): ")
                if id_b is None:
                    break
                brg = df_kat[df_kat["id_barang"] == id_b]
                if brg.empty:
                    print("ID Barang tidak ditemukan!")
                    continue
                sisa = int(brg.iloc[0]["stok"]) - sum(1 for x in keranjang if x["id_barang"] == id_b)
                if sisa <= 0:
                    print("Stok habis atau sudah maksimal di keranjang!")
                    continue
                durasi = input_angka("Durasi sewa (hari) (atau '0' batal): ")
                if durasi is None:
                    break
                harga = int(brg.iloc[0]["harga_per_hari"])
                keranjang.append({
                    "id_barang": id_b,
                    "nama_barang": str(brg.iloc[0]["nama_barang"]),
                    "harga_per_hari": harga,
                    "durasi_hari": durasi,
                    "subtotal": harga * durasi
                })
                print("\nUnit berhasil ditambahkan ke keranjang.")
                jeda()
                break

        elif pilih in ("3", "4"):
            bersihkan_layar()
            print("=== UBAH / HAPUS UNIT KERANJANG ===")
            if not tampilkan_tabel_keranjang(keranjang):
                jeda()
                continue

            while True:
                no = input_angka("\nPilih nomor urut ('no') unit (atau '0' kembali): ")
                if no is None:
                    break
                if no > len(keranjang):
                    print("Nomor urut tidak valid!")
                    continue
                if pilih == "3":
                    dur_baru = input_angka("Durasi sewa baru (hari) (atau '0' batal): ")
                    if dur_baru is not None:
                        keranjang[no - 1]["durasi_hari"] = dur_baru
                        keranjang[no - 1]["subtotal"] = keranjang[no - 1]["harga_per_hari"] * dur_baru
                        print("\nDurasi berhasil diubah.")
                        jeda()
                else:
                    keranjang.pop(no - 1)
                    print("\nUnit berhasil dihapus.")
                    jeda()
                break

        elif pilih == "5":
            bersihkan_layar()
            print("=== KONFIRMASI CHECKOUT SEWA ===")
            if not tampilkan_tabel_keranjang(keranjang):
                jeda()
                continue

            if input("\nKonfirmasi penyewaan sekarang? (y/n): ").strip().lower() == "y":
                df_kat = pd.read_csv(FILE_KATALOG)
                df_tx = pd.read_csv(FILE_TRANSAKSI)

                # Validasi ulang stok sebelum menyimpan agar stok tidak minus
                stok_cukup = True
                for id_unik in set(x["id_barang"] for x in keranjang):
                    jumlah_diminta = sum(1 for x in keranjang if x["id_barang"] == id_unik)
                    baris_brg = df_kat[df_kat["id_barang"] == id_unik]
                    if baris_brg.empty or int(baris_brg.iloc[0]["stok"]) < jumlah_diminta:
                        print(f"\nGagal checkout! Stok untuk ID Barang {id_unik} tidak mencukupi.")
                        stok_cukup = False
                        break

                if not stok_cukup:
                    jeda()
                    continue

                max_id = pd.to_numeric(df_tx["id_transaksi"], errors="coerce").max()
                id_tx_berikutnya = int(max_id) + 1 if pd.notna(max_id) else 1001

                daftar_tx_baru = []
                for item in keranjang:
                    df_kat.loc[df_kat["id_barang"] == item["id_barang"], "stok"] -= 1
                    daftar_tx_baru.append({
                        "id_transaksi": id_tx_berikutnya,
                        "username": username_login,
                        "nama_barang": item["nama_barang"],
                        "durasi_hari": item["durasi_hari"],
                        "total_biaya": item["subtotal"],
                        "status": "Disewa"
                    })
                    id_tx_berikutnya += 1

                df_tx_baru = pd.DataFrame(daftar_tx_baru)
                df_tx = df_tx_baru if df_tx.empty else pd.concat([df_tx, df_tx_baru], ignore_index=True)

                df_kat.to_csv(FILE_KATALOG, index=False)
                df_tx.to_csv(FILE_TRANSAKSI, index=False)
                print("\nTransaksi berhasil! Stok katalog otomatis berkurang.")
                jeda()
                break

        elif pilih == "0":
            break
        else:
            print("Pilihan menu tidak tersedia! Masukkan angka 0-5.")
            jeda()

def riwayat_saya(username_login):
    bersihkan_layar()
    print("=== RIWAYAT SEWA SAYA ===")
    df_tx = pd.read_csv(FILE_TRANSAKSI)
    riwayat = df_tx[df_tx["username"].astype(str).str.lower() == username_login]
    cetak_tabel(riwayat, kolom_rupiah=["total_biaya"])
    jeda()

# ==========================================================
# 3. FITUR ADMIN
# ==========================================================

def kelola_katalog():
    while True:
        bersihkan_layar()
        print("=== KELOLA KATALOG ===")
        lihat_katalog()
        print("\n1. Lihat barang\n2. Tambah barang\n3. Ubah harga & stok\n4. Hapus barang\n0. Kembali")
        pilih = input("\nPilih menu: ").strip()
        df_kat = pd.read_csv(FILE_KATALOG)

        if pilih == "1":
            bersihkan_layar()
            lihat_katalog()
            jeda()

        elif pilih == "2":
            bersihkan_layar()
            print("=== TAMBAH UNIT BARU === (Ketik '0' untuk kembali)")
            lihat_katalog()
            id_b = input_angka("\nID Barang   : ", daftar_duplikat=df_kat["id_barang"].values)
            if id_b is None:
                continue
            nama = input_teks("Nama Barang : ", daftar_duplikat=df_kat["nama_barang"].values)
            if nama is None:
                continue
            while True:
                kat = input("Kategori (iPhone/Kamera): ").strip().lower()
                if kat == "0":
                    kat = None
                    break
                if kat in ("iphone", "kamera"):
                    kat = "iPhone" if kat == "iphone" else "Kamera"
                    break
                print("Kategori hanya boleh 'iPhone' atau 'Kamera'!")
            if kat is None:
                continue
            harga = input_angka("Harga/Hari  : ", minimal=1000)
            stok = input_angka("Jumlah Stok : ", minimal=1) if harga is not None else None
            if stok is None:
                continue

            baru = pd.DataFrame([{
                "id_barang": id_b,
                "nama_barang": nama,
                "kategori": kat,
                "harga_per_hari": harga,
                "stok": stok
            }])
            df_hasil = baru if df_kat.empty else pd.concat([df_kat, baru], ignore_index=True)
            df_hasil.to_csv(FILE_KATALOG, index=False)
            print("\nUnit berhasil ditambahkan.")
            jeda()

        elif pilih in ("3", "4"):
            bersihkan_layar()
            lihat_katalog()
            if df_kat.empty:
                jeda()
                continue
            while True:
                id_t = input_angka("\nMasukkan ID Barang target (atau '0' kembali): ")
                if id_t is None:
                    break
                if id_t not in df_kat["id_barang"].values:
                    print("ID Barang tidak ditemukan!")
                    continue
                if pilih == "3":
                    h_baru = input_angka("Harga baru (atau '0' batal): ", minimal=1000)
                    if h_baru is not None:
                        s_baru = input_angka("Stok baru (atau '0' untuk stok kosong): ", minimal=0)
                        if s_baru is not None:
                            df_kat.loc[df_kat["id_barang"] == id_t, ["harga_per_hari", "stok"]] = [h_baru, s_baru]
                            df_kat.to_csv(FILE_KATALOG, index=False)
                            print("\nData berhasil diubah.")
                            jeda()
                else:
                    if input("Yakin hapus barang ini? (y/n): ").strip().lower() == "y":
                        df_kat[df_kat["id_barang"] != id_t].to_csv(FILE_KATALOG, index=False)
                        print("\nBarang berhasil dihapus.")
                    else:
                        print("\nPenghapusan dibatalkan.")
                    jeda()
                break

        elif pilih == "0":
            break
        else:
            print("Pilihan menu tidak tersedia! Masukkan angka 0-4.")
            jeda()

def kelola_customer():
    while True:
        bersihkan_layar()
        print("=== KELOLA CUSTOMER ===\n1. Lihat customer\n2. Tambah customer\n3. Ubah customer\n4. Hapus customer\n0. Kembali")
        pilih = input("\nPilih menu: ").strip()
        df_u = pd.read_csv(FILE_USERS)
        cust = df_u[df_u["role"] == "customer"]

        if pilih == "1":
            bersihkan_layar()
            print("=== DAFTAR CUSTOMER ===")
            cetak_tabel(cust[["username", "nama", "role"]])
            jeda()
        elif pilih == "2":
            registrasi_customer()
        elif pilih in ("3", "4"):
            bersihkan_layar()
            if cust.empty:
                print("Belum ada customer.")
                jeda()
                continue
            cetak_tabel(cust[["username", "nama", "password"]])
            while True:
                target = input("\nUsername customer target (atau '0' kembali): ").strip().lower()
                if target == "0":
                    break
                if target not in cust["username"].astype(str).str.lower().values:
                    print("Username tidak ditemukan!")
                    continue
                if pilih == "3":
                    n_baru = input("Nama baru (kosongkan jika tetap, '0' batal)     : ").strip()
                    if n_baru == "0":
                        break
                    batal = False
                    while True:
                        p_baru = input("Password baru (kosongkan jika tetap, '0' batal) : ").strip()
                        if p_baru == "0":
                            batal = True
                            break
                        if p_baru and not password_valid(p_baru):
                            print("Password minimal 8 karakter (Kapital, Kecil, Angka, Simbol)!")
                            continue
                        break
                    if batal:
                        break
                    if n_baru:
                        df_u.loc[df_u["username"].astype(str).str.lower() == target, "nama"] = n_baru
                    if p_baru:
                        df_u.loc[df_u["username"].astype(str).str.lower() == target, "password"] = p_baru
                    df_u.to_csv(FILE_USERS, index=False)
                    print("\nData customer diperbarui.")
                else:
                    if input(f"Hapus akun '{target}'? (y/n): ").strip().lower() == "y":
                        df_u[df_u["username"].astype(str).str.lower() != target].to_csv(FILE_USERS, index=False)
                        print("\nAkun berhasil dihapus.")
                    else:
                        print("\nPenghapusan dibatalkan.")
                jeda()
                break
        elif pilih == "0":
            break
        else:
            print("Pilihan menu tidak tersedia! Masukkan angka 0-4.")
            jeda()

def kelola_pengembalian():
    bersihkan_layar()
    print("=== PENGEMBALIAN UNIT ===")
    df_tx = pd.read_csv(FILE_TRANSAKSI)
    aktif = df_tx[df_tx["status"] == "Disewa"]
    cetak_tabel(aktif, kolom_rupiah=["total_biaya"])
    if aktif.empty:
        jeda()
        return

    while True:
        id_tx = input_angka("\nID Transaksi yang dikembalikan (atau '0' kembali): ")
        if id_tx is None:
            break
        cek = df_tx[(df_tx["id_transaksi"] == id_tx) & (df_tx["status"] == "Disewa")]
        if cek.empty:
            print("ID Transaksi tidak valid!")
            continue
        nama_b = str(cek.iloc[0]["nama_barang"])
        df_tx.loc[df_tx["id_transaksi"] == id_tx, "status"] = "Dikembalikan"
        df_tx.to_csv(FILE_TRANSAKSI, index=False)

        df_kat = pd.read_csv(FILE_KATALOG)
        df_kat.loc[df_kat["nama_barang"].astype(str).str.lower() == nama_b.lower(), "stok"] += 1
        df_kat.to_csv(FILE_KATALOG, index=False)
        print(f"\nPengembalian berhasil! Stok '{nama_b}' bertambah +1.")
        jeda()
        break

def pantau_transaksi():
    bersihkan_layar()
    print("=== SELURUH TRANSAKSI ===")
    df_tx = pd.read_csv(FILE_TRANSAKSI)
    cetak_tabel(df_tx, kolom_rupiah=["total_biaya"])
    jeda()

# ==========================================================
# 4. MENU UTAMA
# ==========================================================

def menu_customer(user):
    while True:
        bersihkan_layar()
        print(f"=== MENU CUSTOMER ({user}) ===")
        print("1. Lihat katalog\n2. Cari unit\n3. Keranjang & Sewa\n4. Riwayat sewa\n5. Edit profil\n0. Logout")
        p = input("\nPilih menu: ").strip()
        if p == "1":
            bersihkan_layar()
            lihat_katalog()
            jeda()
        elif p == "2":
            cari_katalog()
        elif p == "3":
            keranjang_sewa(user)
        elif p == "4":
            riwayat_saya(user)
        elif p == "5":
            edit_profil(user)
        elif p == "0":
            break
        else:
            print("Pilihan menu tidak tersedia! Masukkan angka 0-5.")
            jeda()

def menu_admin(user):
    while True:
        bersihkan_layar()
        print(f"=== MENU ADMIN ({user}) ===")
        print("1. Kelola katalog\n2. Kelola customer\n3. Kelola pengembalian\n4. Pantau transaksi\n0. Logout")
        p = input("\nPilih menu: ").strip()
        if p == "1":
            kelola_katalog()
        elif p == "2":
            kelola_customer()
        elif p == "3":
            kelola_pengembalian()
        elif p == "4":
            pantau_transaksi()
        elif p == "0":
            break
        else:
            print("Pilihan menu tidak tersedia! Masukkan angka 0-4.")
            jeda()

def main():
    inisialisasi_berkas()
    while True:
        bersihkan_layar()
        print("=== SISTEM SEWAJA ===\n1. Registrasi Customer\n2. Login\n0. Keluar")
        p = input("\nPilih menu: ").strip()
        if p == "1":
            registrasi_customer()
        elif p == "2":
            user, role = login()
            if role == "customer":
                menu_customer(user)
            elif role == "admin":
                menu_admin(user)
        elif p == "0":
            bersihkan_layar()
            print("Terima kasih telah menggunakan SEWAJA!")
            break
        else:
            print("Pilihan menu tidak tersedia! Masukkan angka 0-2.")
            jeda()

if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram dihentikan dengan aman.")