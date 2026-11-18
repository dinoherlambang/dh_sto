# -*- coding: utf-8 -*-
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    interwarehouse_transfer_id = fields.Many2one(
        "stock.interwarehouse.transfer",
        string="Inter-WH Transfer",
        copy=False,
        index=True,
        help="Dokumen Stock Transfer Order (STO) yang menaungi pergerakan ini.",
    )

    has_interwarehouse_transfer = fields.Boolean(
        string="Memiliki STO",
        compute="_compute_has_interwarehouse_transfer",
        store=True,
        help="Menandakan apakah pergerakan ini terikat dengan dokumen Stock Transfer Order.",
    )

    allow_non_sto_product = fields.Boolean(
        string="Bypass: Izinkan Produk Non-STO",
        default=False,
        tracking=True,
        copy=False,
        help="Otorisasi darurat oleh Supervisor/Manager untuk mengizinkan produk di luar pesanan STO.",
    )

    non_sto_justification = fields.Text(
        string="Alasan Justifikasi Non-STO",
        tracking=True,
        copy=False,
        help="Alasan wajib diisi jika bypass proteksi produk non-STO diaktifkan.",
    )

    # Field Operasional Logistik & Ekspedisi
    send_by = fields.Char(
        string="Send Via / No. Kendaraan",
        copy=False,
        help="Nomor kendaraan atau armada ekspedisi pengiriman.",
    )
    driver_by = fields.Char(
        string="Driver / Sopir",
        copy=False,
        help="Nama pengemudi / driver yang membawa barang.",
    )
    logistic_id = fields.Many2one(
        "res.users",
        string="Logistic By",
        copy=False,
        help="Petugas / penanggung jawab operasional logistik.",
    )

    @api.depends("interwarehouse_transfer_id", "origin")
    def _compute_has_interwarehouse_transfer(self):
        for picking in self:
            sto = picking._get_sto_transfer()
            picking.has_interwarehouse_transfer = bool(sto)

    def _get_sto_transfer(self):
        """Mencari Stock Transfer Order yang terkait dengan picking ini."""
        self.ensure_one()
        if self.interwarehouse_transfer_id:
            return self.interwarehouse_transfer_id
        if self.origin:
            sto = self.env["stock.interwarehouse.transfer"].search(
                [("name", "=", self.origin.strip())], limit=1
            )
            if sto:
                return sto
        return False

    def _get_allowed_sto_products(self):
        """
        Mengembalikan recordset product.product yang sah untuk ditransfer:
        1. Seluruh produk yang terdaftar pada line_ids STO.
        2. Seluruh produk komponen jika terdapat produk bertipe Kit/BOM Phantom atau OCA product-pack.
        """
        self.ensure_one()
        sto = self._get_sto_transfer()
        if not sto:
            return None

        allowed_products = sto.line_ids.mapped("product_id")

        # 1. Komponen OCA product_pack
        for prod in list(allowed_products):
            if getattr(prod, "pack_ok", False) and getattr(prod, "pack_line_ids", False):
                allowed_products |= prod.pack_line_ids.mapped("product_id")

        # 2. Komponen Kit / Phantom BOM (MRP)
        if "mrp.bom" in self.env:
            for prod in list(allowed_products):
                try:
                    boms = self.env["mrp.bom"]._bom_find(
                        product=prod, company_id=self.company_id.id
                    )
                    if boms and boms.type == "phantom":
                        try:
                            _, bom_lines = boms.explode(prod, 1.0)
                            bom_product_ids = [l[0].product_id.id for l in bom_lines]
                            allowed_products |= self.env["product.product"].browse(bom_product_ids)
                        except Exception:
                            allowed_products |= boms.bom_line_ids.mapped("product_id")
                except Exception:
                    pass

        return allowed_products

    def _validate_strict_sto_products(self):
        """
        Validasi ketat terhadap seluruh pergerakan barang (stock.move dan stock.move.line)
        pada dokumen picking pengiriman atau penerimaan antar-gudang (STO).
        """
        for picking in self:
            sto = picking._get_sto_transfer()
            if not sto:
                continue

            # Jika bypass aktif oleh Manager
            if picking.allow_non_sto_product:
                if not picking.non_sto_justification or not picking.non_sto_justification.strip():
                    raise UserError(
                        _(
                            "⛔ [PROTEKSI TRANSFER GUDANG] Alasan Justifikasi Wajib Diisi!\n\n"
                            "Bypass produk non-STO pada dokumen '%s' telah dicentang, "
                            "namun 'Alasan Justifikasi Non-STO' masih kosong.\n"
                            "Harap berikan penjelasan resmi sebelum memvalidasi dokumen."
                        )
                        % picking.name
                    )
                continue

            allowed_products = picking._get_allowed_sto_products()
            if allowed_products is None:
                continue

            # 1. Cek produk tidak sah di stock.move
            unauthorized_moves = picking.move_lines.filtered(
                lambda m: m.state != "cancel" and m.product_id and m.product_id not in allowed_products
            )
            if unauthorized_moves:
                product_list_str = "\n".join(
                    [f"• [{m.product_id.default_code or '-'}] {m.product_id.name}" for m in unauthorized_moves]
                )
                raise UserError(
                    _(
                        "⛔ [PROTEKSI TRANSFER GUDANG] Validasi Ditolak!\n\n"
                        "Produk berikut TIDAK ADA dalam dokumen Stock Transfer Order %s:\n\n"
                        "%s\n\n"
                        "Dokumen mutasi antar-gudang dilarang memuat produk di luar pesanan resmi STO.\n"
                        "Langkah Solusi:\n"
                        "1. Hapus baris produk yang salah dari dokumen ini, ATAU\n"
                        "2. Jika mutasi tambahan/pengganti disetujui, hubungi Supervisor/Manager "
                        "untuk mencentang 'Bypass: Izinkan Produk Non-STO' dan melampirkan alasannya."
                    )
                    % (sto.name, product_list_str)
                )

            # 2. Cek produk tidak sah di stock.move.line (Nomor Seri / Lot)
            unauthorized_smls = picking.move_line_ids.filtered(
                lambda ml: ml.state != "cancel" and ml.product_id and ml.product_id not in allowed_products
            )
            if unauthorized_smls:
                sml_list_str = "\n".join(
                    [
                        f"• [{ml.product_id.default_code or '-'}] {ml.product_id.name} (Lot/Seri: {ml.lot_id.name or ml.lot_name or '-'})"
                        for ml in unauthorized_smls
                    ]
                )
                raise UserError(
                    _(
                        "⛔ [PROTEKSI TRANSFER GUDANG] Validasi Ditolak!\n\n"
                        "Terdapat Nomor Seri / Lot untuk produk yang TIDAK ADA dalam Stock Transfer Order %s:\n\n"
                        "%s\n\n"
                        "Harap hapus baris lot/nomor seri produk yang salah sebelum melanjutkan."
                    )
                    % (sto.name, sml_list_str)
                )

            # 3. Cek over-transfer (kuantitas melebihi persetujuan STO)
            # Khusus untuk outbound picking (pengiriman dari gudang asal)
            if picking.picking_type_id and picking.picking_type_id.code == "outgoing":
                for line in sto.line_ids:
                    ordered_qty = line.product_uom_qty
                    current_picking_moves = picking.move_lines.filtered(
                        lambda m: m.state != "cancel" and m.product_id == line.product_id
                    )
                    current_qty = sum(current_picking_moves.mapped("quantity_done"))
                    # Cek kuantitas yang sudah dikirim di picking lain
                    other_moves = sto.picking_ids.filtered(
                        lambda p: p != picking and p.picking_type_id.code == "outgoing" and p.state == "done"
                    ).mapped("move_lines").filtered(
                        lambda m: m.product_id == line.product_id
                    )
                    shipped_qty = sum(other_moves.mapped("quantity_done"))

                    if (shipped_qty + current_qty) > ordered_qty:
                        raise UserError(
                            _(
                                "⛔ [PROTEKSI TRANSFER GUDANG] Kuantitas Melebihi Persetujuan STO!\n\n"
                                "Produk: %s\n"
                                "Kuantitas STO: %s %s\n"
                                "Sudah Terkirim Sebelumnya: %s %s\n"
                                "Akan Dikirim Saat Ini: %s %s\n\n"
                                "Total pengiriman (%s) melebihi kuantitas yang disetujui pada Stock Transfer Order %s."
                            )
                            % (
                                line.product_id.display_name,
                                ordered_qty,
                                line.product_uom.name,
                                shipped_qty,
                                line.product_uom.name,
                                current_qty,
                                line.product_uom.name,
                                (shipped_qty + current_qty),
                                sto.name,
                            )
                        )

    def button_validate(self):
        """Memastikan pengecekan produk non-STO berjalan sebelum validasi."""
        self._validate_strict_sto_products()
        return super().button_validate()

    def action_assign(self):
        """Cek validasi saat reservasi stok (Check Availability)."""
        self._validate_strict_sto_products()
        return super().action_assign()

    def _create_backorder(self):
        backorders = super()._create_backorder()
        for backorder in backorders:
            backorder.interwarehouse_transfer_id = (
                backorder.backorder_id.interwarehouse_transfer_id
            )
            backorder.send_by = backorder.backorder_id.send_by
            backorder.driver_by = backorder.backorder_id.driver_by
            backorder.logistic_id = backorder.backorder_id.logistic_id
        return backorders
