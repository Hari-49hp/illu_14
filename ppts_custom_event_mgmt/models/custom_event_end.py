import datetime
from odoo import api, fields, models, _

class CustomEventEnd(models.Model):
    _inherit = 'event.event'

    # Automatically move to end state on End date expires

    def event_move_to_end(self):
        publish_type=self.env['event.stage'].search([('name','=','Published')])
        end_type=self.env['event.stage'].search([('name','=','Ended')])
        expired_event_list = self.env['event.event'].search([
            ('date_end', '<', datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")),
            ('stage_id','=',publish_type.id)])
        if expired_event_list:
            for rec in expired_event_list:
                rec.stage_id=end_type.id