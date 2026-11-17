### Panduan Penggunaan

Akses menu melalui: **Inventory > Operations > Stock Transfer Orders (STO)**

1. **Pembuatan STO (Draft):**
   - Klik **Create**.
   - Pilih **From Warehouse** (Gudang Asal) dan **To Warehouse** (Gudang Tujuan).
   - Tentukan **Scheduled Date** (Tanggal Rencana Transfer).
   - Masukkan daftar produk beserta kuantitas pada tab **Products**.
   - Simpan dokumen.

2. **Pengajuan Approval:**
   - Pemohon mengklik tombol **Submit for Approval**.
   - Status STO berubah menjadi **Waiting Approval** (`to_approve`).

3. **Persetujuan (Approval):**
   - Manajer Inventory atau Supervisor memeriksa dokumen.
   - Klik tombol **Approve**.
   - Sistem otomatis membuat 2 dokumen transfer (OUT dan IN) yang dapat dipantau melalui smart button **Transfers**. Status STO berubah menjadi **Approved** (`confirmed`).

4. **Pengiriman dari Gudang Asal (Surat Jalan):**
   - Tim gudang asal memproses dokumen pengeluaran (**Picking OUT**).
   - Validasi Picking OUT setelah barang diberangkatkan.
   - Status STO otomatis berubah menjadi **In Transit** (`in_transit`).

5. **Penerimaan di Gudang Tujuan:**
   - Tim gudang tujuan memeriksa fisik barang yang tiba dan memvalidasi dokumen penerimaan (**Picking IN**).
   - Status STO otomatis berubah menjadi **Done** (`done`).

6. **Pembatalan / Reset:**
   - Dokumen pada status Draft atau Waiting Approval dapat dibatalkan (**Cancel**) atau dikembalikan ke Draft (**Set to Draft**).
