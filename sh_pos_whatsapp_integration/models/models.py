from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_whatsapp = fields.Boolean(string="Enable Whatsapp")
    whatsapp_template_id = fields.Many2one('mail.whatsapp', string='Whatsapp Template')
    broadcast_name = fields.Char('Broadcast Name')


class ResUsers(models.Model):
    _inherit = "res.users"

    sign = fields.Text(string='Signature')
