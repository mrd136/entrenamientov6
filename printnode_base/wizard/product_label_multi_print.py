# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models, api, _


class ProductLabelMultiPrint(models.TransientModel):
    _name = 'product.label.multi.print'
    _inherit = 'printnode.report.abstract.wizard'
    _description = 'Print Product Labels'

    report_id = fields.Many2one(
        comodel_name='ir.actions.report',
        domain=[
            ('model', '=', 'product.product'),
            ('report_type', 'in', ['qweb-pdf', 'qweb-text']),
        ],
        default=lambda self: self.env.ref('stock.label_product_product'),
    )
    product_line_ids = fields.One2many(
        comodel_name='product.label.multi.print.line',
        inverse_name='wizard_id',
        string='Products',
    )

    def _get_printers_from_preferences(self):
        from_user = self.env.user.printnode_printer
        from_company = self.env.company.printnode_printer
        return from_user, from_company

    def _get_allowed_printers(self):
        from_user_rules = self.env['printnode.rule'].search([
            ('user_id', '=', self.env.uid),
            ('report_id.model', '=', 'product.product'),
            ('report_id.report_type', 'in', ['qweb-pdf', 'qweb-text']),
        ]).mapped('printer_id')
        from_user, from_company = self._get_printers_from_preferences()
        return list(set(sum((from_user_rules.ids, from_user.ids, from_company.ids), [])))

    @api.onchange('report_id')
    def _change_wizard_printer(self):
        from_user_rules = self.env['printnode.rule'].search([
            ('user_id', '=', self.env.uid),
            ('report_id', '=', self.report_id.id),
        ], limit=1)
        from_user, from_company = self._get_printers_from_preferences()
        self.printer_id = from_user_rules.printer_id or from_user or from_company

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ProductLabelMultiPrint, self).fields_get()
        res['printer_id']['domain'] = [('id', 'in', self._get_allowed_printers())]
        return res

    def get_action(self):
        self.ensure_one()
        view = self.env.ref('printnode_base.product_label_multi_print_form')
        action = {
            'name': _('Print Product Labels'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.label.multi.print',
            'views': [(view.id, 'form')],
            'target': 'new',
            'res_id': self.id,
        }
        return action

    def get_report(self):
        self.ensure_one()
        return self.report_id

    def get_docids(self):
        self.ensure_one()
        objects = self.env['product.product']

        for line in self.product_line_ids:
            # pylint:disable=W0612
            for i in range(line.quantity):
                objects = objects.concat(line.product_id)
        return objects
