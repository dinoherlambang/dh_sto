# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Transfer Order (STO)",
    "summary": "Internal stock transfer orders between warehouses with approval workflow and two-step fulfillment.",
    "version": "13.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA), Dino",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/stock_interwarehouse_transfer_views.xml",
    ],
    "installable": True,
    "application": True,
}
