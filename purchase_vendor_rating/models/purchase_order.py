from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_rating = fields.Selection([
        (str(num), str(num)) for num in range(1, 6)
    ],
        help="Rate the vendor from 1 to 5 stars.",
        readonly=False,
    )

    vendor_feedback = fields.Text(string="Vendor Feedback", help="Leave feedback for this vendor")
    
