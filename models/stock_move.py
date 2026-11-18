# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    interwh_transfer_line_id = fields.Many2one(
        "stock.interwarehouse.transfer.line",
        string="Inter-WH Transfer Line",
        index=True,
        ondelete="set null",
    )

    # === CONSTRAINT METHODS ===

    @api.constrains("location_id", "location_dest_id", "picking_type_id")
    def _check_inter_warehouse_move(self):
        for move in self:
            if move.picking_type_id.code != "internal":
                continue
            wh_from = move.location_id.warehouse_id
            wh_to = move.location_dest_id.warehouse_id
            if wh_from and wh_to and wh_from != wh_to:
                raise ValidationError(
                    _(
                        "Cannot create an internal move between locations of "
                        "different warehouses (%s → %s). "
                        "Use a Stock Transfer Order (STO) instead."
                    )
                    % (wh_from.name, wh_to.name)
                )

    @api.constrains("product_id", "picking_id")
    def _check_product_against_sto(self):
        for move in self:
            picking = move.picking_id
            if not picking or not getattr(picking, "interwarehouse_transfer_id", False):
                continue
            if getattr(picking, "allow_non_sto_product", False):
                continue
            allowed = picking._get_allowed_sto_products()
            if allowed is not None and move.product_id and move.product_id not in allowed:
                raise ValidationError(
                    _(
                        "⛔ [PROTEKSI TRANSFER GUDANG] Penambahan Produk Ditolak!\n\n"
                        "Produk '[%s] %s' tidak ada dalam Stock Transfer Order %s.\n\n"
                        "Dokumen mutasi antar-gudang dikunci hanya untuk produk yang disetujui di STO."
                    )
                    % (
                        move.product_id.default_code or "-",
                        move.product_id.name,
                        picking.interwarehouse_transfer_id.name,
                    )
                )

    # === CORE METHODS ===

    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("interwh_transfer_line_id")
        return distinct_fields

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        transfer = self.interwh_transfer_line_id.transfer_id
        if len(transfer) == 1:
            vals["interwarehouse_transfer_id"] = transfer.id
            if transfer.send_by:
                vals["send_by"] = transfer.send_by
            if transfer.driver_by:
                vals["driver_by"] = transfer.driver_by
            if transfer.logistic_id:
                vals["logistic_id"] = transfer.logistic_id.id
        return vals
