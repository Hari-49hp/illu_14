from datetime import date, datetime, timedelta, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class EventReject(models.TransientModel):
    _name = "event.reject"
    _description = 'Event Reject'

    description = fields.Text("Description")
    reject_reason_id = fields.Many2one('event.reject.master',string="Reason",required=True)

    # pass the reject reason value
    def action_reject_reason(self):
        active_id = self._context.get('active_id')
        rec = self.env["event.event"].browse(active_id)
        rec.reject_value = True
        rec.reject_reason_id = self.reject_reason_id.id
        rec.reject_desc = self.description
        rec.reject_id = self.env.user.id 
        rec.reject_on = datetime.now()
        get_event_stage_id = self.env['event.stage'].search([('is_reject','=',True)],limit=1)
        if get_event_stage_id:
            rec.stage_id = get_event_stage_id.id
        # send mail to event creator while reject the event
        template_id = self.env.ref('ppts_custom_event_mgmt.event_reject_mail_template')
        if template_id:
            template_id.send_mail(rec.id,force_send=True)
    