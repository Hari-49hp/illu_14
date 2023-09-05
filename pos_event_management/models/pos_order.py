from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = 'pos.order'

    event_reg_id = fields.Many2one('event.registration',string='Event Ref')
    
class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    event_reg_id = fields.Many2one('event.registration',string='Event Ref',related="order_id.event_reg_id")
