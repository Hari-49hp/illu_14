from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    availability_minimum_mail = fields.Integer('Availability Hours Required')

    interval_number = fields.Integer('Interval Number')
    interval_type = fields.Selection([('minutes','Minutes'),('hours','Hours'),('days','Days'),('weeks','Weeks')],'Interval Type')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        obj_interval_number = (ICPSudo.get_param('custom_event_mail.interval_number'))
        obj_interval_type = (ICPSudo.get_param('custom_event_mail.interval_type'))
        obj_availability_minimum_mail = (ICPSudo.get_param('custom_event_mail.availability_minimum_mail'))        
        res.update(
            interval_number=obj_interval_number,
            interval_type=obj_interval_type,
            availability_minimum_mail=obj_availability_minimum_mail,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("custom_event_mail.interval_number", self.interval_number)
        ICPSudo.set_param("custom_event_mail.interval_type", self.interval_type)
        ICPSudo.set_param("custom_event_mail.availability_minimum_mail", self.availability_minimum_mail)