# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class PrintNodeActionButton(models.Model):
    """ Call Button
    """
    _name = 'printnode.action.button'
    _description = 'PrintNode Action Button'

    _rec_name = 'report_id'

    active = fields.Boolean(
        'Active', default=True,
        help="""Activate or Deactivate the print action button.
                If no active then move to the status \'archive\'.
                Still can by found using filters button"""
    )

    description = fields.Char(
        string='Description',
        size=64,
        help="""Text field for notes and memo."""
    )

    model_id = fields.Many2one(
        'ir.model',
        string='Model'
    )

    model = fields.Char(
        string='Related Document Model',
        related='model_id.model',
        help="""Choose a model where the button is placed. You can find the
                model name in the URL. For example the model of this page is
                \'model=printnode.action.button\'.
                Check this in the URL after the \'model=\'."""
    )

    method = fields.Char(
        string='Method',
        size=64
    )

    method_id = fields.Many2one(
        'printnode.action.method',
        string='Method ID',
        help="""The technical name of the action that a button performs.
                It can be seen only in debug mode. Hover the cursor on
                the desired button using debug mode and type a method name
                in this field."""
    )

    report_id = fields.Many2one(
        'ir.actions.report',
        string='Report',
        help="""Choose a report that will be printed after you hit a button"""
    )

    printer_id = fields.Many2one(
        'printnode.printer',
        string='Printer'
    )

    preprint = fields.Boolean(
        'Print before action',
        help="""By default the report will be printed after your action.
                First you click a button, server make the action then print
                result of this. If you want to print first and only after
                that make an action assigned to the button, then activate
                this field. Valid per each action (button)."""
    )

    domain = fields.Text(
        string='Domain',
        default='[]',
    )

    def _get_model_objects(self, ids_list):
        self.ensure_one()
        related_model = self.env[self.model]
        if self.domain == '[]':
            return related_model.browse(ids_list)
        return related_model.search(
            expression.AND([[('id', 'in', ids_list)], eval(self.domain)])
        )

    def _get_action_printer(self):
        self.ensure_one()
        user = self.env.user
        printer = self.printer_id \
                  or user.printnode_printer \
                  or user.company_id.printnode_printer
        if not printer:
            raise UserError(_(
                'Neither on action button level, no on user level, no on company level '
                'printer is defined for method "%s". Please, define it.'
                % self.method_id.name
            ))
        return printer

    def edit_domain(self):
        domain_editor = self.env.ref(
            'printnode_base.printnode_domain_editor',
            raise_if_not_found=False,
        )
        action = {
            'name': _('Domain Editor'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'printnode.action.button',
            'res_id': self.id,
            'view_id': domain_editor.id,
            'target': 'self',
        }
        return action


class PrintNodeActionMethod(models.Model):
    """
    """
    _name = 'printnode.action.method'
    _description = 'PrintNode Action Method'

    name = fields.Char(
        string='Name',
        size=64
    )

    model_id = fields.Many2one(
        'ir.model',
        string='Model'
    )

    method = fields.Char(
        string='Method',
        size=64
    )

    @api.constrains('method')
    def _check_skip_method(self):
        su = self.env['ir.config_parameter'].sudo()
        methods_list = su.get_param('printnode_base.skip_methods', '').split(',')
        for action_method in self:
            if action_method.method in methods_list:
                raise ValidationError(_(
                    'The following methods are not supported: {}'.format(methods_list)
                ))
