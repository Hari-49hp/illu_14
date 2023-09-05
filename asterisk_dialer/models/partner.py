from datetime import datetime
from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    lead_customer = fields.Boolean('Lead Customer',help="to track how customer created")
    