# -*- coding: utf-8 -*-
# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.constrains("product_id", "picking_id")
    def _check_move_line_against_sto(self):
        for line in self:
            picking = line.picking_id
            if not picking or not getattr(picking, "interwarehouse_transfer_id", False):
                continue
            if getattr(picking, "allow_non_sto_product", False):
                continue
            allowed = picking._get_allowed_sto_products()
            if allowed is not None and line.product_id and line.product_id not in allowed:
                lot_info = (
                    f" (No. Seri/Lot: {line.lot_id.name or line.lot_name})"
                    if (line.lot_id or line.lot_name)
                    else ""
                )
                raise ValidationError(
                    _(
                        "⛔ [PROTEKSI TRANSFER GUDANG] Penambahan Nomor Seri/Lot Ditolak!\n\n"
                        "Produk '[%s] %s'%s tidak terdaftar dalam Stock Transfer Order %s.\n\n"
                        "Sistem memblokir penambahan lot/nomor seri produk yang tidak sesuai dengan persetujuan STO."
                    )
                    % (
                        line.product_id.default_code or "-",
                        line.product_id.name,
                        lot_info,
                        picking.interwarehouse_transfer_id.name,
                    )
                )
