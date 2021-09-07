# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import models, fields, _
from odoo.exceptions import UserError


class User(models.Model):
    """ User entity. Add 'Default Printer' field (no restrictions).
    """
    _inherit = 'res.users'

    printnode_enabled = fields.Boolean(
        string='Print via PrintNode',
        default=False
    )

    printnode_printer = fields.Many2one(
        'printnode.printer',
        string='Default Printer'
    )

    user_label_printer = fields.Many2one(
        'printnode.printer',
        string='Shipping Label Printer'
    )

    def __init__(self, pool, cr):
        init_res = super(User, self).__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend([
            'printnode_enabled',
            'printnode_printer',
            'user_label_printer',
        ])
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend([
            'printnode_enabled',
            'printnode_printer',
            'user_label_printer',
        ])
        return init_res

    def _get_shipping_label_printer(self):
        company = self.company_id

        printer = self.user_label_printer or company.company_label_printer
        if not printer:
            raise UserError(_(
                'Neither on company level, no on user level default label printer '
                'is defined. Please, define it.'
            ))
        return printer
