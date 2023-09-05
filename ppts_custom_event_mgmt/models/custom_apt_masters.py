from odoo import api, fields, models, _


class ApointmentMainCateg(models.Model):
    _inherit = 'appointment.category'
    
    is_event_sub_category = fields.Boolean('Event SubCategory',help="Is Event SubCateg")
    event_categ_id = fields.Many2one('event.type',string='Event Category', required=True)


    