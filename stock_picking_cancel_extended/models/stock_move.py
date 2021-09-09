# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api,  models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date, OrderedSet
#from _tkinter import create


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    
    def action_cancel_quant_create(self):
        quant_obj = self.env['stock.quant']
        for move in self:
            price_unit = move.get_price_unit()
            location = move.location_id
            rounding = move.product_id.uom_id.rounding
            vals = {
                'product_id': move.product_id.id,
                'location_id': location.id,
                'qty': float_round(move.product_uom_qty, precision_rounding=rounding),
                'cost': price_unit,
                'in_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': move.company_id.id,
            }
            quant_obj.sudo().create(vals)
            return
        
    
    def action_draft(self):
        for task in self:
            task.write({'state': 'draft'})

    def _do_unreserve(self):
        moves_to_unreserve = OrderedSet()
        for move in self:
            if self._context.get('stock_cancel') == True:
                pass
            else:
                if move.state == 'cancel' or (move.state == 'done' and move.scrapped):
                    # We may have cancelled move in an open picking in a "propagate_cancel" scenario.
                    # We may have done move in an open picking in a scrap scenario.
                    continue
                elif move.state == 'done':
                    raise UserError(_("You cannot unreserve a stock move that has been set to 'Done'."))
            moves_to_unreserve.add(move.id)

        moves_to_unreserve = self.env['stock.move'].browse(moves_to_unreserve)

        ml_to_update, ml_to_unlink = OrderedSet(), OrderedSet()
        moves_not_to_recompute = OrderedSet()
        for ml in moves_to_unreserve.move_line_ids:
            if self._context.get('stock_cancel',False) == True:
                ml_to_unlink.add(ml.id)
                moves_not_to_recompute.add(ml.move_id.id)
            elif ml.qty_done:
                ml_to_update.add(ml.id)
            else:
                ml_to_unlink.add(ml.id)
                moves_not_to_recompute.add(ml.move_id.id)
        
        self._recompute_state()

        ml_to_update, ml_to_unlink = self.env['stock.move.line'].browse(ml_to_update), self.env['stock.move.line'].browse(ml_to_unlink)
        moves_not_to_recompute = self.env['stock.move'].browse(moves_not_to_recompute)

        ml_to_update.write({'product_uom_qty': 0})
        print ('___ ml_to_unlink : ', ml_to_unlink)
        ml_to_unlink.with_context(stock_cancel=True).unlink()
        # `write` on `stock.move.line` doesn't call `_recompute_state` (unlike to `unlink`),
        # so it must be called for each move where no move line has been deleted.
        (moves_to_unreserve - moves_not_to_recompute)._recompute_state()
        return True
    

    def _action_cancel(self):
        print ('___ self._context : ', self._context)
        if self._context.get('inventory') == True:
            pass
        elif self._context.get('stock_cancel') == True:
            pass
        else:
            if any(move.state == 'done' and not move.scrapped for move in self):
                raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'. Create a return in order to reverse the moves which took place.'))
        
        moves_to_cancel = self.filtered(lambda m: m.state != 'cancel')
        # self cannot contain moves that are either cancelled or done, therefore we can safely
        # unlink all associated move_line_ids
        moves_to_cancel.with_context(stock_cancel=True)._do_unreserve()

        for move in moves_to_cancel:
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids.filtered(lambda m: m.state != 'done')._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        
        self.write({
            'state': 'cancel',
            'move_orig_ids': [(5, 0, 0)],
            'procure_method': 'make_to_stock',
        })
        return True
    
    def _action_cancel_done(self):
        '''if any(move.state == 'done' for move in self):
            raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'.'))'''
        for move in self:
            move.with_context(stock_cancel=True)._do_unreserve()
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
            
            if move.quantity_done:

                if move.picking_id.picking_type_id.code in ['outgoing','internal']:
                        
                        for move_id in move:
                            for line in move_id.move_line_ids:
                                                                            
                                if move.location_dest_id.usage == 'customer':
                                    outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
                                    stock_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
                                    if outgoing_quant:
                                        old_qty = outgoing_quant[0].quantity
                                        outgoing_quant[0].quantity = old_qty - move.product_uom_qty
                                        abc = outgoing_quant[0].quantity
                                    if stock_quant:
                                        old_qty = stock_quant[0].quantity
                                        stock_quant[0].quantity = old_qty + move.product_uom_qty
                                else:
                                    outgoing_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
                                    
                                    if outgoing_quant:
                                        old_qty = outgoing_quant[0].quantity
                                        
                                        outgoing_quant[0].quantity = old_qty + move.product_uom_qty
                                        
                                    outgoing_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
                                    if outgoing_customer_quant:
                                        
                                        old_qty = outgoing_customer_quant[0].quantity
                                        outgoing_customer_quant[0].quantity = old_qty - move.product_uom_qty
                                        
                if move.picking_id.picking_type_id.code == 'incoming':
                    for move_id in move:
                        for line in move_id.move_line_ids:
                            if line.lot_id:
                                if line.product_id.tracking == 'lot':
                                    incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id),('lot_id','=',line.lot_id.id)])
                                    incoming_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
                                    if incoming_quant:
                                        old_qty = incoming_quant[0].quantity
                                        incoming_quant[0].quantity = old_qty - move.product_uom_qty
                                    if incoming_customer_quant:
                                        old_qty = incoming_customer_quant[0].quantity
                                        incoming_customer_quant[0].quantity = old_qty + move.product_uom_qty
                                else:
                                    incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id),('lot_id','=',line.lot_id.id)])
                                    for lot in incoming_quant:
                                        old_qty = lot.quantity
                                        lot.unlink()
                                        vals = { 'product_id' :move.product_id.id,
                                                 'location_id':move.location_dest_id.id,
                                                 'quantity': old_qty,
                                                 'lot_id':line.lot_id.id,
                                               }
                                        test = self.env['stock.quant'].sudo().create(vals)
                            else:
                                incoming_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_dest_id.id)])
                                if incoming_quant:
                                    old_qty = incoming_quant[0].quantity
                                    incoming_quant[0].quantity = old_qty - move.product_uom_qty
                                incoming_customer_quant = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('location_id','=',move.location_id.id)])
                                if incoming_customer_quant:
                                    old_qty = incoming_customer_quant[0].quantity
                                    incoming_customer_quant[0].quantity = old_qty + move.product_uom_qty


                    
            account_move = self.env['account.move'].sudo().search([('stock_move_id','=',move.id)],order="id desc", limit=1)
            
            if account_move : 
                account_move.button_cancel()
            self.write({'state': 'cancel', 'move_orig_ids': [(5, 0, 0)]})
        return True


