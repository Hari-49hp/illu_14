from odoo import api, fields, models, _

class CustomEventReschdule(models.Model):
    _inherit = 'event.event'

    reschedule_enable=fields.Boolean('Reschedule Active')
    event_reschdule_ids=fields.One2many('event.reschedule.info.line','event_reschdule_id',string='Event History')

    def create_reschedule(self):
        f_list_id=[]
        for i in self.facilitator_evnt_ids:
            f_list_id.append(i.id)
        for rec in self:
            rec.stage_id=1
            rec.reschedule_enable = True
            rec.is_published = False
            self.event_publish = False
            resch_id = rec.env['event.reschedule.info.line'].create({'event_reschdule_id':rec.id,
                                                                'rs_name': rec.name,
                                                                'rs_event_type_id': rec.event_type_id.id,
                                                                'rs_date_begin': rec.date_begin,
                                                                'rs_date_end': rec.date_end,
                                                                'rs_address_id': rec.address_id.id,
                                                                'rs_therapist_ids':  [(6, 0, f_list_id)],
                                                                })
        if self.event_meeting_room_id:
            self.event_meeting_room_id.unlink()
        return True

class EventReschdule(models.Model):
    _name = 'event.reschedule.info.line'
    _description="EventReschdule"

    event_reschdule_id=fields.Many2one('event.event')
    rs_name = fields.Char(string='Event')
    rs_event_type_id = fields.Many2one('event.type', string='Type of Event')
    rs_date_begin = fields.Datetime(string='Start Date')
    rs_date_end = fields.Datetime(string='End Date')
    rs_address_id = fields.Many2one('venue.venue', string='Venue')
    # many2one field is not used
    rs_therapist_id = fields.Many2one('hr.employee', string='Facilitator')
    #new many2many field added
    rs_therapist_ids = fields.Many2many('hr.employee', string='Facilitators')
