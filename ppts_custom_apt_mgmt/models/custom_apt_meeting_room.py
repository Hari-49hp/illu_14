from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ApptMeetingRoom(models.Model):
    _inherit = 'event.meeting.room'

    room_max_capacity = fields.Selection(string="Max capacity", related="chat_room_id.max_capacity", readonly=False,required=True)
    event_id = fields.Many2one("event.event", string="Event", required=False, ondelete="cascade")
    name = fields.Char("Topic", required=True, translate=True)
    appointment_id = fields.Many2one('appointment.appointment', string='Appointment',help='Name of Appointment')
    apt_therapist_id = fields.Many2one('hr.employee',string='Therapist',help='Appointment Therpist Name')
    apt_start_dt = fields.Datetime(string='Appointment Start Date',help='Appointment Start Date')
    apt_end_dt = fields.Datetime(string='Appointment End Date',store=True,help='Appointment End Date')
    apt_location_id = fields.Many2one('venue.venue', string='Location',help='Location of Appointment')
    apt_max_seats = fields.Integer(string='Max. Capacity', default=1,help='Maximum limit of Attendees for Appointment')
    apt_duration = fields.Float('Duration', readonly=True, help='Duration of the Appointment.')

    @api.onchange('appointment_id')
    def _compute_name_topic_apt(self):
        self.name=self.appointment_id.name
        self.room_max_capacity='no_limit'

    @api.onchange('booking_types')
    def _compute_booking_types(self):
        self.event_id = 1

from odoo.addons.http_routing.models.ir_http import slug
#
# class EventMeetingRoom(models.Model):
#     _inherit = "event.meeting.room"
#
#     website_url = fields.Char(string="Event", required=True, ondelete="cascade", tracking=True)
#
#     name = fields.Char("Topic", required=True, translate=True, tracking=True)
#     active = fields.Boolean('Active', default=True, tracking=True)
#     is_published = fields.Boolean(copy=True, tracking=True)  # make the inherited field copyable
#     event_id = fields.Many2one("event.event", string="Event", required=False, ondelete="cascade", tracking=True)
#     is_pinned = fields.Boolean("Is Pinned", tracking=True)
#     chat_room_id = fields.Many2one("chat.room", required=True, ondelete="restrict", tracking=True)
#     summary = fields.Char("Summary", translate=True, tracking=True)
#     target_audience = fields.Char("Audience", translate=True, tracking=True)
    #
    # @api.depends('name', 'event_id.name')
    # def _compute_website_url(self):
    #     super(EventMeetingRoom, self)._compute_website_url()
    #     for meeting_room in self:
    #         dfsd
    #         if meeting_room.id:
    #             base_url = meeting_room.event_id.get_base_url()
    #             meeting_room.website_url = '%s/event/%s/meeting_room/%s' % (
    #             base_url, slug(meeting_room.event_id), slug(meeting_room))
    #
    # @api.model_create_multi
    # def create(self, values_list):
    #     for values in values_list:
    #         print('chat_room_id',values.chat_room_id)
    #         print('room_name',values.room_name)
    #
    #         if not values.get("chat_room_id") and not values.get('room_name'):
    #             values['room_name'] = 'odoo-room-%s' % (values['name'])
    #     return super(EventMeetingRoom, self).create(values_list)
