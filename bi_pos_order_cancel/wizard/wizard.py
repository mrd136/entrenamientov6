from odoo import models,fields,api
from odoo.exceptions import UserError, AccessError

class MassCancelTransferPos(models.TransientModel):
	_name = 'mass.cancel.wizard'

	mass_cancel = fields.Boolean(required=True)


	def on_click(self):
		pos_order=self.env["pos.order"].browse(self._context.get('active_ids',[]))
		if self.mass_cancel == False:
			raise UserError(('Please give permission by clicking the check-box to cancel selected pos order.'))

		for order in pos_order:
			if order.state not in ['draft','done']:
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
			else:
				raise UserError(('Unable to cancel pos order as some orders have already been done or in draft.'))


class MassCancelDraftTransferPos(models.TransientModel):
	_name = 'mass.cancel.draft.wizard'

	mass_cancel_draft = fields.Boolean(required=True)


	def on_click(self):
		pos_order=self.env["pos.order"].browse(self._context.get('active_ids',[]))
		if self.mass_cancel_draft == False:
			raise UserError(('Please give permission by clicking the check-box to cancel and reset to draft selected pos order.'))

		for order in pos_order:
			if order.state not in ['draft','done']:
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
			else:
				raise UserError(('Unable to cancel pos order as some orders have already been done or in draft.'))

			if order.state == 'cancel':
				for picking in order.picking_ids:
					picking.action_cancel_draft()
				order.write({'state': 'draft'})
				order.amount_paid = 0.00
				if order.account_move.state == 'cancel':
					order.account_move.button_draft()
			else:
				raise UserError(('You can not set pos order to draft as some orders are not canceled.'))
