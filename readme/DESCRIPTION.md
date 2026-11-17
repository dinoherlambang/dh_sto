# Stock Transfer Order (STO) - `dh_sto`

Modul ini menyediakan dokumen **Stock Transfer Order (STO)** sebagai dasar resmi untuk menjalankan transfer barang antar-gudang (*Internal Transfer*) dalam satu perusahaan.

Mirip dengan prinsip kerja *Sales Order (SO)* yang menjadi dasar penerbitan *Delivery Order (DO)* ke pelanggan, modul ini memastikan bahwa **tim gudang/inventory hanya dapat mengeksekusi transfer barang apabila ada STO yang telah disetujui (Approved)** oleh pihak berwenang.

### Fitur Utama
1. **Siklus Approval Bertahap:** Mendukung alur *Draft* -> *Waiting Approval* -> *Approved* -> *In Transit* -> *Done*.
2. **Otomatisasi 2-Langkah (Two-Step Transfer):** Saat STO disetujui, sistem secara otomatis menerbitkan 2 dokumen terhubung melalui lokasi *Transit Internal*:
   - **Picking OUT** di gudang asal (sebagai Surat Jalan / Delivery Order pengeluaran).
   - **Picking IN** di gudang tujuan (sebagai Bukti Penerimaan Barang / Goods Receipt).
3. **Pencegahan Mutasi Ilegal (Guardrail):** Memblokir mutasi internal manual antar-gudang pada level `stock.move`, sehingga seluruh pergerakan barang antar-gudang wajib memiliki referensi STO.
4. **Pelacakan Fisik di Perjalanan (In-Transit):** Menjaga akurasi nilai persediaan saat barang sedang dikirim dan belum sampai di tujuan.
