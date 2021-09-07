# -*- coding: utf-8 -*-
import datetime
import calendar
from odoo import api, fields, models

MONTHS = [
    ('1', 'Enero'),
    ('2', 'Febrero'),
    ('3', 'Marzo'),
    ('4', 'Abril'),
    ('5', 'Mayo'),
    ('6', 'Junio'),
    ('7', 'Julio'),
    ('8', 'Agosto'),
    ('9', 'Septiembre'),
    ('10', 'Octubre'),
    ('11', 'Noviembre'),
    ('12', 'Diciembre')
]


class SalesJournalReportWizard(models.TransientModel):
    _name = 'sales.journal.report.wizard'
    _description = 'Libro Diario'

    from_month = fields.Selection(MONTHS, string="Mes")
    x_sucursal = fields.Selection(
                    [('Palmeras', 'Palmeras'),
                    ('Santa Lucia', 'Santa Lucia'),
                    ('Tiquisate', 'Tiquisate')
                    ], string="Sucursal")
    company_id = fields.Many2one('res.company', string='Compañia', default=lambda self: self.env.company.id)
    is_used_journal = fields.Boolean(related='company_id.is_used_journal')
    folio = fields.Char(string="Folio")

    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
            # 'ids': [],
            'form': data,
            'month': self.from_month,
            'month_name': calendar.month_name[int(self.from_month)],
            'year': datetime.date.today().year,
            'folio': self.folio,
            'sucursal': self.x_sucursal,    
        }
        return self.env.ref('sales_journal_report.action_report_sales_journal').report_action(self, data=datas)
