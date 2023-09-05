from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    server_url = fields.Char('Server URL')
    access_token = fields.Char('Access Token')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        obj_server_url = (ICPSudo.get_param('ppts_watsapp_integration.server_url'))
        obj_access_token = (ICPSudo.get_param('ppts_watsapp_integration.access_token'))
        
        res.update(
            server_url=obj_server_url,
            access_token=obj_access_token,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("ppts_watsapp_integration.server_url", self.server_url)
        ICPSudo.set_param("ppts_watsapp_integration.access_token", self.access_token)