# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError


class pos_order(models.Model):
    _inherit = "pos.order"

    def pos_order_cancel(self):
        for order in self:
            if order.session_id.state != 'closed':
                order.picking_ids.action_cancel()
                order.action_pos_order_cancel()
                
                if order.account_move.state == 'posted' :

                    order.account_move.line_ids.remove_move_reconcile()


                    order.account_move.button_draft()
                    order.account_move.button_cancel()
                  
                else : 
                    order.account_move.button_draft()
                    order.account_move.button_cancel()

                if order.payment_ids:
                    for statement in order.payment_ids:
                        
                        statement.unlink()

            if order.session_id.state == 'closed':
                order.picking_ids.action_cancel()
                order.action_pos_order_cancel()
                if order.account_move.state == 'posted' :

                    order.account_move.line_ids.remove_move_reconcile()


                    order.account_move.button_draft()
                    order.account_move.button_cancel()
                  
                else : 
                    order.account_move.button_draft()
                    order.account_move.button_cancel()

                if order.payment_ids:
                    for statement in order.payment_ids:
                        
                        statement.unlink()

    def action_draft(self):
        for order in self:
            for picking in order.picking_ids:
                picking.action_cancel_draft()
            order.write({'state': 'draft'})
            order.amount_paid = 0.00
            if order.account_move.state == 'cancel':
                order.account_move.button_draft()

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _confirm_orders(self):
        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(lambda order: order.state == 'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id, default=session.config_id.journal_id.id)
            if not journal_id:
                raise UserError(_("You have to set a Sale Journal for the POS:%s") % (session.config_id.name,))

            move = self.env['pos.order'].with_context(force_company=company_id)._create_account_move(session.start_at, session.name, int(journal_id), company_id)
            orders.with_context(force_company=company_id)._create_account_move_line(session, move)
            for order in session.order_ids.filtered(lambda o: o.state not in ['done', 'invoiced','cancel']):
                if order.state not in ('paid'):
                    raise UserError(
                        _("You cannot confirm all orders of this session, because they have not the 'paid' status.\n"
                          "{reference} is in state {state}, total amount: {total}, paid: {paid}").format(
                            reference=order.pos_reference or order.name,
                            state=order.state,
                            total=order.amount_total,
                            paid=order.amount_paid,
                        ))
                order.action_pos_order_done()
            orders_to_reconcile = session.order_ids._filtered_for_reconciliation()
            orders_to_reconcile.sudo()._reconcile_payments()
