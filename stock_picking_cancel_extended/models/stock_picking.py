# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api,  models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
#from _tkinter import create

class Picking(models.Model):
    _inherit = 'stock.picking'

    
    def action_cancel_draft(self):
        if not len(self.ids):
            return False
        move_obj = self.env['stock.move']
        for (ids, name) in self.name_get():
            message = _("Picking '%s' has been set in draft state.") % name
            self.message_post(body=message)
        for pick in self:
            ids2 = [move.id for move in pick.move_lines]
            moves = move_obj.browse(ids2)
            moves.sudo().action_draft()
        return True


    
    def action_cancel(self):
        for line in self :
            line.mapped('move_lines').with_context(stock_cancel=True)._action_cancel()
            line.write({'is_locked': True})
            # else:
            #     line.mapped('move_lines').with_context(stock_cancel=True)._action_cancel()
            #     line.write({'is_locked': True})
            # account_move = self.env['account.move'].search([('ref','=',line.name)])
            # account_move.with_context(stock_cancel=True).button_cancel()
            # account_move.sudo().with_context(stock_cancel=True).unlink()
        return True

