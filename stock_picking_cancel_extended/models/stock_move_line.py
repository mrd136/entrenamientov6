# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api,  models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
#from _tkinter import create


class stock_move_line(models.Model):
    _inherit = "stock.move.line"
    
    def unlink(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for ml in self:
            if self._context.get('stock_cancel') == True:

                if ml.product_id.type == 'product' and not ml._should_bypass_reservation(ml.location_id) and not float_is_zero(ml.product_qty, precision_digits=precision):
                    self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
            else:
                if ml.state in ('done', 'cancel'):
                    raise UserError(_('You can not delete product moves if the picking is done. You can only correct the done quantities.'))
                # Unlinking a move line should unreserve.
                if ml.product_id.type == 'product' and not ml._should_bypass_reservation(ml.location_id) and not float_is_zero(ml.product_qty, precision_digits=precision):
                    self.env['stock.quant']._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

        moves = self.mapped('move_id')

        if self._context.get('stock_cancel') == True:
            pass 
        else:
            return super(stock_move_line,self).unlink()

        if moves:
            moves.with_prefetch()._recompute_state()

        return models.Model.unlink(self)


