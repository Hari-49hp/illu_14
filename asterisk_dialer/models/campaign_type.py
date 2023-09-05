# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError

logger = logging.getLogger(__name__)


class CampaignType(models.Model):
    _name = "campaign.type"
    _description = "Campaign Type"
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)





