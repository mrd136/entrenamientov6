# Copyright 2019 VentorTech OU
# License OPL-1.0 or later.

from odoo import fields, models 


class Company(models.Model):
    _inherit = 'res.company'

    printnode_enabled = fields.Boolean(
        string='Print via PrintNode',
        default=False
    )

    printnode_printer = fields.Many2one(
        'printnode.printer',
        string='Printer'
    )

    printnode_recheck = fields.Boolean(
        string='Mandatory check Printing Status',
        default=False
    )

    company_label_printer = fields.Many2one(
        'printnode.printer',
        string='Shipping Label Printer'
    )

    auto_send_slp = fields.Boolean(
        string='Auto-send to Shipping Label Printer',
        default=False
    )

    im_a_teapot = fields.Boolean(
        string='Show success notifications',
        default=True
    )


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    printnode_enabled = fields.Boolean(
        string='Print via PrintNode',
        readonly=False,
        related='company_id.printnode_enabled'
    )

    printnode_printer = fields.Many2one(
        'printnode.printer',
        string='Printer',
        readonly=False,
        related='company_id.printnode_printer'
    )

    printnode_recheck = fields.Boolean(
        string='Mandatory check Printing Status',
        readonly=False,
        related='company_id.printnode_recheck'
    )

    company_label_printer = fields.Many2one(
        'printnode.printer',
        string='Shipping Label Printer',
        readonly=False,
        related='company_id.company_label_printer'
    )

    auto_send_slp = fields.Boolean(
        string='Auto-send to Shipping Label Printer',
        readonly=False,
        related='company_id.auto_send_slp'
    )

    im_a_teapot = fields.Boolean(
        string='Show success notifications',
        readonly=False,
        related='company_id.im_a_teapot'
    )
