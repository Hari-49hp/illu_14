from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pytz
from collections import OrderedDict




class Event(models.Model):
    _inherit = "event.event"
    _order = 'date_begin desc'

    
    events_therapist = fields.Text(string="Facilitator Name Raw Values", store=True, compute="_compute_update_default_vals")
    event_days = fields.Text(string="Event Days",store=True,compute="_compute_get_date")
   
    @api.depends('facilitator_evnt_ids','room_id','stage_id')
    def _compute_update_default_vals(self):
        events_desc = []
        for rec in self.facilitator_evnt_ids:
            events_desc.append(rec.name)
        self.events_therapist = (', '.join(events_desc))

    # add the selected days for the event based on date 27-07-22
    @api.depends('facilitator_evnt_ids','room_id','stage_id')
    def _compute_get_date(self):
        events_desc = []
        for rec in self.multi_date_line_ids:
            get_date = rec.date_begin.strftime("%A")
            events_desc.append(get_date[0:3])
            # to remove the duplicate valus in the list 01-08-22
            self.event_days = (', '.join(list(OrderedDict.fromkeys(events_desc))))
      



