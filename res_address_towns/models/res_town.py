from odoo import api, fields, models, tools, _
from odoo.osv import expression


class ResTowns(models.Model):
    _name = 'res.town'
    _description = 'Address Town'

    code = fields.Char('Code')
    name = fields.Char('Name', required=True)
    state_id = fields.Many2one('res.country.state', 'State')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    town_id = fields.Many2one("res.town", string='Town', ondelete='restrict',
                               domain="[('state_id', '=?', state_id)]")
