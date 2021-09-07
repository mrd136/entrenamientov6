# -*- coding: utf-8 -*-
import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportSalesJournal(models.AbstractModel):
    _name = 'report.sales_journal_report.report_sales_journal'
    _description = 'Account Sales Journal Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        sales_journal = self.env['ir.actions.report']._get_report_from_name('sales_journal_report.report_sales_journal')

        from_month = data['form']['from_month']
        xSucursal = data['form']['x_sucursal']
        companyId = data['form']['company_id']

        if xSucursal:
            self.env.cr.execute(
                '''SELECT id
                FROM 
                    account_move
                WHERE
                    state = 'posted' AND
                    EXTRACT(MONTH FROM date) = %s AND
                    x_sucursal = %s AND
                    company_id = %s
                ORDER BY id DESC;''',
                (from_month, xSucursal, companyId[0]))
            moveIDs = [x['id'] for x in self.env.cr.dictfetchall()]
        else:
            self.env.cr.execute(
                '''SELECT id
                FROM 
                    account_move
                WHERE
                    state = 'posted' AND
                    EXTRACT(MONTH FROM date) = %s AND
                    company_id = %s
                ORDER BY id DESC;''',
                (from_month, companyId[0]))
            moveIDs = [x['id'] for x in self.env.cr.dictfetchall()]

        acMove = self.env['account.move'].browse(moveIDs)

        return {
            'doc_model': sales_journal.model,
            'doc_ids': self.ids,
            'docs': self.ids,
            'get_month': data['month'],
            'get_month_name': data['month_name'],
            'get_year': data['year'],
            'get_folio': data['folio'],
            'get_move': acMove,
            'get_sucursal': data['sucursal'],
        }
