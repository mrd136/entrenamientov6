# -*- coding: utf-8 -*-
from odoo import api, models, _, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_used_journal = fields.Boolean(string="Use in Journal?", default=True)
