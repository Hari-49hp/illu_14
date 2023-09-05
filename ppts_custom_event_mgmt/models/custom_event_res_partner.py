from odoo import api, fields, models, _


class CustompartnerLoc(models.Model):
    _inherit = 'res.partner'

    location_flag = fields.Boolean(string='Use for Location', default=False)
