===========================
Stock Transfer Order (STO)
===========================

Modul **`dh_sto`** (Stock Transfer Order) untuk **Odoo 13.0** menyediakan dokumen dasar resmi untuk mengeksekusi transfer barang antar-gudang (*Internal Transfer*).

Konsep modul ini mirip dengan prinsip kerja *Sales Order (SO)* yang menjadi dasar penerbitan *Delivery Order (DO)* ke pelanggan: **tim gudang/inventory hanya dapat mengeksekusi pengiriman barang antar-gudang apabila ada STO yang telah disetujui (Approved)**.

Fitur Utama
===========

* **Siklus Persetujuan (Approval Workflow):**
  Mendukung alur otorisasi berjenjang:
  ``Draft`` → ``Waiting Approval`` → ``Approved`` → ``In Transit`` → ``Done``.

* **Otomatisasi Dua Langkah (Two-Step Transfer):**
  Saat STO disetujui, sistem secara otomatis menerbitkan dua dokumen transfer terhubung melalui lokasi internal transit:
  
  1. **Picking OUT:** Pengeluaran barang di gudang asal (Surat Jalan / DO Transfer).
  2. **Picking IN:** Penerimaan barang di gudang tujuan (Goods Receipt).

* **Penguncian Mutasi Ilegal (Guardrail):**
  Memblokir mutasi internal langsung (*ad-hoc direct move*) antar-gudang yang berbeda pada level ``stock.move``. Pengguna dipaksa untuk selalu melalui dokumen STO resmi.

* **Pelacakan Fisik di Perjalanan (In-Transit Tracking):**
  Memastikan nilai persediaan tidak hilang atau terdistorsi saat barang masih berada dalam perjalanan antar-cabang.

* **Form Sederhana & Ringan (Zero Bloat):**
  Form bebas dari field komersial yang tidak relevan (tidak ada harga jual, margin, termin pembayaran, atau pajak).

Alur Penggunaan
===============

1. **Pembuatan STO:**
   Masuk ke menu **Inventory > Operations > Stock Transfer Orders (STO)**, klik **Create**, lalu pilih Gudang Asal (*From Warehouse*), Gudang Tujuan (*To Warehouse*), Tanggal Rencana, serta daftar produk dan kuantitasnya.

2. **Pengajuan Approval:**
   Klik tombol **Submit for Approval**. Status STO berpindah ke ``Waiting Approval``.

3. **Persetujuan (Approval):**
   Manajer Inventory memeriksa permintaan dan mengklik **Approve**. Sistem otomatis membuat dokumen *Picking OUT* dan *Picking IN*. Status STO berpindah ke ``Approved``.

4. **Pengiriman (Outbound):**
   Tim gudang asal memproses dan memvalidasi *Picking OUT* saat barang diberangkatkan. Status STO otomatis berpindah ke ``In Transit``.

5. **Penerimaan (Inbound):**
   Tim gudang tujuan memvalidasi *Picking IN* saat fisik barang tiba. Status STO otomatis berpindah ke ``Done``.

Spesifikasi Teknis
==================

* **Versi Odoo:** 13.0
* **Dependensi:** ``stock``
* **Kode Sequence:** ``STO/%(year)s/XXXXX``
* **Penulis:** Dino (dikembangkan dari konsep arsitektur ForgeFlow S.L. & OCA)
