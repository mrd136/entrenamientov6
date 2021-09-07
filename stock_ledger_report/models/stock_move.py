from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    quantity_done = fields.Float(store=True)
