from odoo import api, fields, models, _
from datetime import datetime,date

class CustomCalendar(models.Model):
    _inherit = 'calendar.event'
    
    booking_type = fields.Selection([('facilitator', 'Facilitator'),('Appointment', 'Appointment'),
        ('room', 'Room'),('event', 'Event')],string='Booking Type', copy=False,tracking=True)
    name_facilitator = fields.Many2one('hr.employee', string='Facilitator', tracking=True)
    name_event = fields.Many2one('event.event', string='Event', copy=False, tracking=True)
    start_duration = fields.Float('Start Duration')
    end_duration = fields.Float('End Duration')
    room_id = fields.Many2one('roomtype.master',string="Room")
    du_start_light = fields.Char('start Light')
    du_end_light = fields.Char('end Light')
