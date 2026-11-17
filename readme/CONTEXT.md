### Latar Belakang & Kebutuhan Bisnis

Pada operasional multi-gudang, perpindahan barang antar-cabang atau dari gudang pusat ke cabang membutuhkan kontrol ketat untuk mencegah selisih stok (*shrinkage*) dan pengiriman tanpa otorisasi.

Di Odoo standar, mutasi internal dilakukan langsung di dokumen `stock.picking` tanpa adanya dokumen pemesanan (*order/request*) yang memiliki alur persetujuan (*approval*).

### Pendekatan Solusi (`dh_sto`)

Modul `dh_sto` memperkenalkan lapisan **Stock Transfer Order (STO)**:
- Berdiri sendiri (*standalone*) dan hanya bergantung pada modul standar `stock`.
- Form sederhana dan fokus pada kebutuhan logistik murni, tanpa beban komersial (tidak ada harga jual, margin, atau pajak yang membingungkan staf gudang).
- Memisahkan peran antara pemohon (cabang), penyetujui (manajer inventory), dan eksekutor (tim operasional gudang).
