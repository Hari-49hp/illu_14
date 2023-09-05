import base64
import requests
from odoo import api, fields, models, _
from dateutil import rrule
import re
import pytz
import babel.dates
from odoo import tools
from odoo.exceptions import UserError,ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import get_lang
from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import time
import werkzeug

class CustomEvent(models.Model):
    _inherit = 'event.event'

    address_id = fields.Many2one('venue.venue', string='Venue',tracking=True,help='Location of the Event')
    event_type_id = fields.Many2one('event.type', string='Template', ondelete='set null',help='Type of Event')
    seats_limited = fields.Boolean('Maximum Attendees', required=True, compute='_compute_seats_limited',
                                   readonly=False, store=True,  default=True,help='Limit of Maximum Attendees')
    events_type = fields.Many2one('eventtype.master',string='Event Type', copy=False,tracking=True,help='Type of Event')
    class_level_id = fields.Many2one('event.class.level',string='Event Format', copy=False,tracking=True,help='Type of Event')
    evnt_maincateg = fields.Many2one('event.maincateg.master',string='Main Category', copy=False,tracking=True,help='Event Main Category')
    evnt_subcateg = fields.Many2one('event.subcateg.master', string=' Event SubCategory', copy=False,tracking=True,help='Event Sub Category')
    eve_therapist_id = fields.Many2one('hr.employee',string=' Facilitator',help='Name of Therapist')
    facilitator_evnt_ids=fields.Many2many('hr.employee','hr_facilitator_evnt_ids',string='Facilitator ',help='List of Facilitators Name',domain="[('id','in',emp_type_ids),('company_id','=',company_id)]")
    evnt_assistant = fields.Many2many('hr.employee', relation='m2m_assistant_rel', column1='event_tbl_id',
                                        column2='employee_id', string='Assistant',tracking=True,help='List of Assistants for the event')
    evnt_description = fields.Html(string='Event Description',tracking=True,help='Description about the Event')
    evnt_location = fields.Many2one('res.company',string='Event Location',tracking=True,help='Location of event')
    evnt_online_limit = fields.Integer(string='How many people can book online?',tracking=True,help='Limit of Online Booking')
    evnt_waitlist_limit = fields.Integer(string='How many can waitlist?',tracking=True,help='Limit of Waiting List')
    evnt_offline_limit = fields.Integer(string='How many people can book offline?', store=True,tracking=True,help='Limit of Offline Booking')
    evnt_weblink = fields.Char(string='Web Link',tracking=True,help='Web URL of Online Type Events. E.g: Zoom Link, Online Video URL')
    evnt_notes = fields.Text(string='Internal Notes',tracking=True,help='Additional Notes about Event')
    sale_incharge_id = fields.Many2one('res.users', string='Sales In-charge', tracking=True,help='The person who is Sales In-charge of event.')
    evnt_meeting_loc = fields.Char(string='Meeting point of Location', tracking=True,help='Event Meeting Point Info')
    dress_code = fields.Char(string='Dress Code', tracking=True,help='Dress code info if any for the Events')
    contact_person = fields.Many2one('hr.employee',string='Contact Person', tracking=True,help='Additional Contact person for the events.')
    #image
    event_img_url = fields.Char(string='Image URL',store=True,tracking=True,help='Image Location of Images stored in Cloud.')
    event_img = fields.Binary('Event Image', attachment=True)
    #Days Selection
    duration = fields.Float('Duration',help='Duration of the Event')
    eve_early_cancel = fields.Integer('Early Cancel',default=1)
    eve_interval_range = fields.Selection([('months','Month'),('day','Day')],string="range",default="months")
    eve_cancel_charge = fields.Float(string="Early Cancel Charge")
    allday = fields.Boolean('All Day', default=False)
    event_publish = fields.Boolean(string='Publish Online')
    event_external = fields.Boolean(string='Additional Notes')
    # online / off-line type
    type_event =fields.Selection([('type_online', 'Online'),('type_onsite', 'Onsite'),
        ('type_hybrid', 'Onsite/Online')], string='Type of Event?',help='Type of event to specify Online/ Offline/ Hybrid')
    type_online = fields.Selection([
        ('type_live', 'Online Live'),
        ('type_record', 'Online- Recorded videos')], string='Online Category',help='Sub categroy of Online Type Events')
    rrule = fields.Char('Recurrent Rule', store=True)
    rrule_type = fields.Selection([('daily', 'Days'),('weekly', 'Weeks'),('monthly', 'Months'),('yearly', 'Years')], string='Recurrence', help="Let the event automatically repeat at that interval")
    recurrency = fields.Boolean('Recurrent ', help="Recurrent Meeting")
    recurrent_id = fields.Integer('Recurrent ID')
    recurrent_id_date = fields.Datetime('Recurrent ID date')
    end_type = fields.Selection([('count', 'Number of repetitions'), ('end_date', 'End date')], string='Recurrence Termination', default='count')
    interval = fields.Integer(string='Repeat Every', default=1, help="Repeat every (Days/Week/Month/Year)")
    count = fields.Integer(string='Repeat', help="Repeat x times", default=1)
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    month_by = fields.Selection([('date', 'Date of month'),('day', 'Day of month')], string='Option', default='date')
    day = fields.Integer('Date of month', default=1)
    week_list = fields.Selection([('MO', 'Monday'),('TU', 'Tuesday'),('WE', 'Wednesday'),('TH', 'Thursday'),('FR', 'Friday'),('SA', 'Saturday'),('SU', 'Sunday')], string='Weekday')
    byday = fields.Selection([('1', 'First'),('2', 'Second'),('3', 'Third'),('4', 'Fourth'),('5', 'Fifth'),('-1', 'Last')], string='By day')
    final_date = fields.Date('Repeat Until')
    hosted_by = fields.Many2one('res.users',string="Hosted By")
    event_meeting_room_id = fields.Many2one('event.meeting.room',string="Event Meeting Room")
    tag_by_healing_id = fields.Many2one('tag.by.healing', string='Tag By Healing')
    tag_by_sub_healing_id = fields.Many2one('tag.by.sub.healing', string='Tag By Sub Healing', domain="[('parent_id','=',tag_by_healing_id)]")
    tag_by_therapy_id = fields.Many2one('tag.by.therapy', string='Tag By Therapy', domain="[('parent_id','=',tag_by_healing_id)]")
    tag_by_therapy_ids = fields.Many2many('tag.by.therapy','event_tag_therapy_ref','event_therapy_id','tag_id', string='Tag By Therapy', domain="[('parent_id','=',tag_by_healing_id)]")
    approver_id = fields.Many2one('res.users',string="Approver")
    event_seq = fields.Char(readonly=True, copy=False, default=' ',tracking=True)
    multiday = fields.Boolean(default=False)
    calendar_id = fields.Many2one('calendar.event',string="Calendar")
    event_id = fields.Many2one('event.event',string="Event ")
    # compute_date = fields.Char('dummy empty',compute='_compute_date_compare')
    event_start = fields.Date(string="Start Date")
    event_end = fields.Date(string="End Date")
    start_end_date = fields.Boolean(string="Multidate Invisible",help="Help to invisible the start date and end date for multidate concepts")
    is_ended = fields.Boolean(String="Is Ended ",help="Help to make readonly cancellation charges fields")
    emp_type_ids = fields.Many2many('hr.employee',string="Employee Types",compute="compute_set_facilitator_domain")

    @api.depends('facilitator_evnt_ids','event_multiple_date')
    def compute_set_facilitator_domain(self):
        therapist_ids=self.env['hr.employee.category'].search([('name', 'ilike','Facilitator')])
        get_facilitator = self.env['hr.employee'].search([('employee_type','in',therapist_ids.ids)])
        self.emp_type_ids = get_facilitator.ids
    

    def event_registration(self):
        if not self.stage_id.is_published :
            raise UserError(_('Event is not Published, So you cannot register'))
        view = self.env.ref('ppts_event_registration_view.action_client_registrations')
        return {
            'name': _('Attendees'),
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban',
            'res_model': 'event.event',
            'target': 'current',
            'domain': [('id', '=', self.id)],
            'context': {'default_id': self.id,'search_default_expected': True,'default_partner_id': False},
        }

    @api.model
    def create(self, vals):
        if vals.get('event_seq', ' ') == ' ':
            vals['event_seq'] = self.env['ir.sequence'].next_by_code('event.event') or ' '
        res = super(CustomEvent, self).create(vals)
        # call the single date event onchange function 01-8-22
        # res._onchangeddd_min_time_end()
        if res.event_multiple_date == 'oneday':
            date = str(res.s_start_date) + str(res.hour_time_begin) + " : " + str(res.min_time_begin) +  " to " + str(res.hour_time_end) + " : " + str(res.min_time_end)
        else:
            date = str(res.date_begin) + "To" + str(res.date_end)            
        msg_body = """Creation Date : """ + str(res.create_date.date()) + """ <br/> """ +\
           """Event Name : """ + str(res.name) + """ <br/> """ +\
           """Event Days : """ + str(dict(res._fields['event_multiple_date'].selection).get(res.event_multiple_date) or 'N/A') + """ <br/> """ +\
           """Event Date : """ + date +  """ <br/> """ +\
           """Duration : """ + str(res.duration or 'N/A') + """ <br/> """ +\
           """Venue : """ + str(res.address_id.name or 'N/A') + """ <br/> """ +\
           """Event Category : """ + str(res.event_type_id.name or 'N/A') + """ <br/> """ +\
           """Sub Category : """ + str(res.event_sub_categ_id.name or 'N/A') + """ <br/> """ +\
           """Event Platform : """ + str(dict(res._fields['type_event'].selection).get(res.type_event) or 'N/A') + """ <br/> """ +\
           """Sales Incharge : """ + str(res.sale_incharge_id.name or 'N/A') + """ <br/> """ 
        res.message_post(body=msg_body)

        # Send mail to the creator while create the event 15-06-22

        template_id = self.env.ref('ppts_custom_event_mgmt.event_approver_mail_template')
        if template_id:
            template_id.send_mail(res.id,force_send=True)

        return res

        # added the event reject button

    def action_event_reject(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Reject Reason',
                'view_mode': 'form',
                'res_model': 'event.reject',
                'target':'new'
                }

    def action_register(self):
        view = self.env.ref('event.view_event_registration_form')
        return {
            'name': _('Attendees'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'event.registration',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': {'default_event_id': self.id,'default_partner_id': False},

        }

    @api.onchange('s_start_date','duration')
    def _onchange_s_start_date(self):
        if self.event_multiple_date == 'oneday' and self.hour_time_begin and self.min_time_begin and self.hour_time_end and self.min_time_end: 
            self.date_begin = str(self.s_start_date) + " " + str(self.hour_time_begin) + ":" + str(self.min_time_begin) + ":" + str("00")
            self.date_end = str(self.s_start_date) + " " +str(self.hour_time_end) + ":" + str(self.min_time_end) + ":" + str("00")
            print(self.date_end,self.date_begin)
        else:
            self.date_begin = False
            self.date_end = False

    @api.onchange('multi_date_line_ids','event_multiple_date','s_start_date')
    def onchange_facilitator_evnt_ids_reset(self):
        if self.facilitator_evnt_ids:
            self.facilitator_evnt_ids =False
            # Set values below field has been empty while changing the date 04-07-22
            self.hour_time_begin = False
            self.min_time_begin = False
            self.hour_time_end = False
            self.min_time_end = False
            self.duration = False

        if self.room_id:
            self.room_id=False



    @api.onchange('multi_date_line_ids','duration','facilitator_evnt_ids')
    def onchange_facilitator_evnt_ids_set(self):
        res = {'domain': {'facilitator_evnt_ids': "[('id', 'not in', False)]"}}
        line_ids = []
        for each_date in self.multi_date_line_ids:
            availability = self.env['availability.availability'].search([('available_date','=',datetime.strftime(each_date.date_begin, "%Y-%m-%d"))])
            for i in availability:
                if i.facilitator.id not in line_ids:
                    line_ids.append(i.facilitator.id)
        # fac_id = self.env['hr.employee.category'].search(['|',('name','=','Facilitator')],limit=1)
        # for line in self.env['hr.employee'].search([('employee_type','in',fac_id.id),('id','in',line_ids)]):
        #     facilitator_ids.append(line.id)
        res['domain']['facilitator_evnt_ids'] = "[('id', 'in', %s)]" % line_ids
        return res

    def onchange_image_url(self):
        """ function to load image from URL in product variant"""
        image = False
        if self.event_img_url:
            image = base64.b64encode(requests.get(self.event_img_url).content)
        self.event_img = image

    @api.onchange("event_type_id")
    def _compute_event_external(self):
        for rec in self:
            if rec.event_type_id:
                if rec.event_type_id.name =='External Event':
                    rec.event_external = True
                else:
                    rec.event_external = False

    @api.onchange("date_begin")
    def _compute_date_compare_oc(self):
        if self.date_begin:
            cur_dt = datetime.strftime(self.date_begin, "%d/%m/%Y %H:%M:%S")
            cur_dt_now = datetime.strftime(datetime.now(), "%d/%m/%Y %H:%M:%S")
            pcur_dt = datetime.strptime(cur_dt, "%d/%m/%Y %H:%M:%S")
            pcur_dt_now = datetime.strptime(cur_dt_now, "%d/%m/%Y %H:%M:%S")
            if pcur_dt < pcur_dt_now:
                raise UserError('Back Date & Time for Event Not Allowed!')

    @api.onchange('facilitator_evnt_ids')
    def _eve_therapist_id(self):
        if self.facilitator_evnt_ids:
            for each_date in self.multi_date_line_ids:
                therapist_exists =self.env['multi.date.line'].search([('event_id.facilitator_evnt_ids' , 'in',self.facilitator_evnt_ids.ids),('event_id','!=', False),('event_id.id','!=',self._origin.id),
                                                                ('m_date_begin', '<=', each_date.m_date_begin), ('m_date_end', '>=', each_date.m_date_end)])
                if therapist_exists: 
                    self.multi_date_line_ids = False
                    self.date_begin = False
                    self.date_end = False
                    raise UserError("This Facilitator is allocated to another event at this Time ")
                if not therapist_exists:
                    multi_date =self.env['multi.date.line'].search([('event_id.facilitator_evnt_ids' , 'in',self.facilitator_evnt_ids.ids),('event_id','!=', False),('event_id.id','!=',self._origin.id)])
                    if multi_date:
                        for each_multi_date in multi_date:
                            if each_date.m_date_begin <= each_multi_date.m_date_begin <= each_date.m_date_end:
                                raise UserError("This Facilitator is allocated to another event at this Time ")
                            if each_date.m_date_begin <= each_multi_date.m_date_end <= each_date.m_date_end:
                                raise UserError("This Facilitator is allocated to another event at this Time ")
                appointment_ids =self.env['appointment.appointment'].search([('state','not in',('cancel','void')),('booking_date','!=',False),('booking_date','=',each_date.date_begin),('therapist_id','in',self.facilitator_evnt_ids.ids)])
                for each_apt in appointment_ids:                    
                    timezone = pytz.timezone(self.env.user.tz or 'UTC')
                    date_begin = each_date.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                    date_end = each_date.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                    # change validation functionality based on the appointment 03-8-22
                    if each_apt.start_time_str and each_apt.end_time_str:
                        if date_begin.strftime("%H:%M") <= each_apt.start_time_str:
                            if date_begin.strftime("%H:%M") <= each_apt.start_time_str and each_apt.start_time_str < date_end.strftime("%H:%M"):
                                raise UserError(_("This Facilitator is allocated to another Appointment at this time. \n Facilitator Name - %s \n Appointment Reference - %s" % (each_apt.therapist_id.name,each_apt.sequence)))
                            if date_begin.strftime("%H:%M") <= each_apt.end_time_str and each_apt.end_time_str  < date_end.strftime("%H:%M"):
                                raise UserError(_("This Facilitator is allocated to another Appointment at this time. \n Customer Name - %s \n Appointment Reference - %s" % (each_apt.therapist_id.name,each_apt.sequence)))

                        if date_begin.strftime("%H:%M") > each_apt.start_time_str:
                            if date_begin.strftime("%H:%M") >= each_apt.start_time_str and date_begin.strftime("%H:%M") < each_apt.end_time_str:
                                raise UserError(_("This Facilitator is allocated to another Appointment at this time. \n Facilitator Name - %s \n Appointment Reference - %s" % (each_apt.therapist_id.name,each_apt.sequence)))

                        # if each_apt.start_time_str <= date_begin.strftime("%H:%M") <= each_apt.end_time_str:
                        #     raise UserError("This Facilitator is allocated to another Appointment at this Time")
                        # if each_apt.start_time_str <= date_end.strftime("%H:%M") <= each_apt.end_time_str:
                        #     raise UserError("This Facilitator is allocated to another Appointment at this Time")

    @api.onchange('room_id')
    def onchange_room_id(self):
        multi_date= False
        for each_date in self.multi_date_line_ids:
            room_exists =self.env['multi.date.line'].search([('event_id.room_id' , '=',self.room_id.id),('event_id','!=', False),('event_id.id','!=',self._origin.id),
                                                            ('m_date_begin', '<=', each_date.m_date_begin), ('m_date_end', '>=', each_date.m_date_end)])
            if room_exists: 
                self.multi_date_line_ids = False
                self.date_begin = False
                self.date_end = False
                raise UserError("This Room is allocated to another event at this Time ")
            if not room_exists:
                multi_date =self.env['multi.date.line'].search([('event_id.room_id' , '=',self.room_id.id),('event_id','!=', False),('event_id.id','!=',self._origin.id)])                
                if multi_date:
                    for each_multi_date in multi_date:
                        if each_date.m_date_begin <= each_multi_date.m_date_begin <= each_date.m_date_end:
                            raise UserError("This Room is allocated to another event at this Time ")
                        if each_date.m_date_begin <= each_multi_date.m_date_end <= each_date.m_date_end:
                            raise UserError("This Room is allocated to another event at this Time ")
            appointment_ids =self.env['appointment.appointment'].search([('state','not in',('cancel','void')),('booking_date','!=',False),('apt_room_id','=',self.room_id.id)])
            for each_apt in appointment_ids:
                if each_apt.booking_date == each_date.date_begin:
                    timezone = pytz.timezone(self.env.user.tz or 'UTC')
                    date_begin = each_date.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                    date_end = each_date.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                    if each_apt.start_time_str and each_apt.end_time_str:
                        if each_apt.start_time_str <= date_begin.strftime("%H:%M") <= each_apt.end_time_str:
                            raise UserError("This Room is allocated to another Appointment at this Time")
                        if each_apt.start_time_str <= date_end.strftime("%H:%M") <= each_apt.end_time_str:
                            raise UserError("This Room is allocated to another Appointment at this Time")


    def open_google_map(self):
        params = {
            'q': '%s,%s, %s %s, %s' % (
            self.address_id.street or '', self.address_id.street2 or '', self.address_id.city or '', self.address_id.zip or '', self.address_id.country_id and self.address_id.country_id.display_name or ''),
            'z': 10,
        }
        return {'name': 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type': 'ir.actions.act_url',
                'target': 'new',
                'url': 'https://maps.google.com/maps?'+ werkzeug.urls.url_encode(params)
                }


    def unlink(self):
        for event in self:
            if not event.stage_id.is_waiting:
                raise UserError(_("You cannot delete an Event."))
        return super(CustomEvent, self).unlink()

    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time) according to start/stop fields and allday. Also, compute
            the duration for not allday meeting ; otherwise the duration is set to zero, since the meeting last all the day.
        """
        for meeting in self:
            if meeting.allday and meeting.start and meeting.stop:
                meeting.start_date = meeting.start.date()
                meeting.start_datetime = False
                meeting.stop_date = meeting.stop.date()
                meeting.stop_datetime = False
                meeting.duration = 0.0
            else:
                meeting.start_date = False
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop
                meeting.duration = self._get_duration(meeting.start, meeting.stop)

    def _inverse_dates(self):
        for meeting in self:
            if meeting.allday:
                # Convention break:
                # stop and start are NOT in UTC in allday event
                # in this case, they actually represent a date
                # i.e. Christmas is on 25/12 for everyone
                # even if people don't celebrate it simultaneously
                enddate = fields.Datetime.from_string(meeting.stop_date)
                enddate = enddate.replace(hour=18)
                startdate = fields.Datetime.from_string(meeting.start_date)
                startdate = startdate.replace(hour=8)  # Set 8 AM
                meeting.write({
                    'start': startdate.replace(tzinfo=None),
                    'stop': enddate.replace(tzinfo=None)
                })
            else:
                meeting.write({'start': meeting.start_datetime,
                               'stop': meeting.stop_datetime})

    @api.depends('byday', 'recurrency', 'final_date', 'rrule_type', 'month_by', 'interval', 'count', 'end_type', 'mo',
                 'tu', 'we', 'th', 'fr', 'sa', 'su', 'day', 'week_list')
    def _compute_rrule(self):
        """ Gets Recurrence rule string according to value type RECUR of iCalendar from the values given.
            :return dictionary of rrule value.
        """
        for meeting in self:
            if meeting.recurrency:
                meeting.rrule = meeting._rrule_serialize()
            else:
                meeting.rrule = ''

    def _inverse_rrule(self):
        for meeting in self:
            if meeting.rrule:
                data = self._rrule_default_values()
                data['recurrency'] = True
                data.update(self._rrule_parse(meeting.rrule, data, meeting.start))
                meeting.update(data)

    def _rrule_serialize(self):
        """ Compute rule string according to value type RECUR of iCalendar
            :return: string containing recurring rule (empty if no rule)
        """
        if self.interval <= 0:
            raise UserError(_('The interval cannot be negative.'))
        if self.end_type == 'count' and self.count <= 0:
            raise UserError(_('The number of repetitions  cannot be negative.'))

        def get_week_string(freq):
            weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
            if freq == 'weekly':
                byday = [field.upper() for field in weekdays if self[field]]
                if byday:
                    return ';BYDAY=' + ','.join(byday)
            return ''

        def get_month_string(freq):
            if freq == 'monthly':
                if self.month_by == 'date' and (self.day < 1 or self.day > 31):
                    raise UserError(_("Please select a proper day of the month."))

                if self.month_by == 'day' and self.byday and self.week_list:  # Eg : Second Monday of the month
                    return ';BYDAY=' + self.byday + self.week_list
                elif self.month_by == 'date':  # Eg : 16th of the month
                    return ';BYMONTHDAY=' + str(self.day)
            return ''

        def get_end_date():
            final_date = fields.Date.to_string(self.final_date)
            end_date_new = ''.join((re.compile('\d')).findall(final_date)) + 'T235959Z' if final_date else False
            return (self.end_type == 'count' and (';COUNT=' + str(self.count)) or '') +\
                ((end_date_new and self.end_type == 'end_date' and (';UNTIL=' + end_date_new)) or '')

        freq = self.rrule_type  # day/week/month/year
        result = ''
        if freq:
            interval_string = self.interval and (';INTERVAL=' + str(self.interval)) or ''
            result = 'FREQ=' + freq.upper() + get_week_string(freq) + interval_string + get_end_date() + get_month_string(freq)
        return result

    def _rrule_default_values(self):
        return {
            'byday': False,
            'recurrency': False,
            'final_date': False,
            'rrule_type': False,
            'month_by': False,
            'interval': 0,
            'count': False,
            'end_type': False,
            'mo': False,
            'tu': False,
            'we': False,
            'th': False,
            'fr': False,
            'sa': False,
            'su': False,
            'day': False,
            'week_list': False
        }

    def _rrule_parse(self, rule_str, data, date_start):
        day_list = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        rrule_type = ['yearly', 'monthly', 'weekly', 'daily']
        ddate = fields.Datetime.from_string(date_start)
        if 'Z' in rule_str and not ddate.tzinfo:
            ddate = ddate.replace(tzinfo=pytz.timezone('UTC'))
            rule = rrule.rrulestr(rule_str, dtstart=ddate)
        else:
            rule = rrule.rrulestr(rule_str, dtstart=ddate)
        if rule._freq > 0 and rule._freq < 4:
            data['rrule_type'] = rrule_type[rule._freq]
        data['count'] = rule._count
        data['interval'] = rule._interval
        data['final_date'] = rule._until and rule._until.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        #repeat weekly
        if rule._byweekday:
            for i in range(0, 7):
                if i in rule._byweekday:
                    data[day_list[i]] = True
            data['rrule_type'] = 'weekly'
        #repeat monthly by nweekday ((weekday, weeknumber), )
        if rule._bynweekday:
            data['week_list'] = day_list[list(rule._bynweekday)[0][0]].upper()
            data['byday'] = str(list(rule._bynweekday)[0][1])
            data['month_by'] = 'day'
            data['rrule_type'] = 'monthly'
        if rule._bymonthday:
            data['day'] = list(rule._bymonthday)[0]
            data['month_by'] = 'date'
            data['rrule_type'] = 'monthly'
        #repeat yearly but for odoo it's monthly, take same information as monthly but interval is 12 times
        if rule._bymonth:
            data['interval'] = data['interval'] * 12
        #FIXEME handle forever case
        #end of recurrence
        #in case of repeat for ever that we do not support right now
        if not (data.get('count') or data.get('final_date')):
            data['count'] = 100
        if data.get('count'):
            data['end_type'] = 'count'
        else:
            data['end_type'] = 'end_date'
        return data

    def get_interval(self, interval, tz=None):
        """ Format and localize some dates to be used in email templates
            :param string interval: Among 'day', 'month', 'dayname' and 'time' indicating the desired formatting
            :param string tz: Timezone indicator (optional)
            :return unicode: Formatted date or time (as unicode string, to prevent jinja2 crash)
        """
        self.ensure_one()
        date = fields.Datetime.from_string(self.start)
        if tz:
            timezone = pytz.timezone(tz or 'UTC')
            date = date.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
        if interval == 'day':
            # Day number (1-31)
            result = str(date.day)
        elif interval == 'month':
            # Localized month name and year
            result = babel.dates.format_date(date=date, format='MMMM y', locale=get_lang(self.env).code)
        elif interval == 'dayname':
            # Localized day name
            result = babel.dates.format_date(date=date, format='EEEE', locale=get_lang(self.env).code)
        elif interval == 'time':
            # Localized time
            # FIXME: formats are specifically encoded to bytes, maybe use babel?
            dummy, format_time = self._get_date_formats()
            result = tools.ustr(date.strftime(format_time + " %Z"))
        return result

    def get_display_time_tz(self, tz=False):
        self.ensure_one()
        if tz:
            self = self.with_context(tz=tz)
        return self._get_display_time(self.start, self.stop, self.duration, self.allday)

    def detach_recurring_event(self, values=None):
        """ Detach a virtual recurring event by duplicating the original and change reccurent values
            :param values : dict of value to override on the detached event
        """
        if not values:
            values = {}
        real_id = calendar_id2real_id(self.id)
        meeting_origin = self.browse(real_id)
        data = self.read(['allday', 'start', 'stop', 'rrule', 'duration'])[0]
        if data.get('rrule'):
            data.update(values, recurrent_id=real_id, recurrent_id_date=data.get('start'), rrule_type=False, rrule='',
                recurrency=False, final_date=False, end_type=False)
            if data.get('id'):
                del data['id']
            return meeting_origin.with_context(detaching=True).copy(default=data)

    def action_detach_recurring_event(self):
        meeting = self.detach_recurring_event()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'res_id': meeting.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    @api.onchange('date_begin','date_end','multi_date_line_ids','event_multiple_date')
    def _onchange_duration_event(self):
        for rec in self:    
            def diff(t_a, t_b):
                t_diff = relativedelta(t_b, t_a)  # later/end time comes first!
                return str(t_diff.hours)+':'+str(t_diff.minutes)+':'+str(t_diff.seconds)
            h = []
            dates_list=[]
            for i in rec.multi_date_line_ids:
                dates_list.append(i.m_date_begin)
                dates_list.append(i.m_date_end)
                a = datetime(2022, 1, 18, int(i.hour_time_begin), int(i.min_time_begin), 00)
                b = datetime(2022, 1, 18, int(i.hour_time_end), int(i.min_time_end), 00)                    
                h.append(diff(a,b))            
            def to_td(h):
                ho, mi, se = h.split(':')
                return timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))
            totalSecs = 0
            hr = 0
            minutes =0
            for tm in h:
                timeParts = [int(s) for s in tm.split(':')]
                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
            totalSecs, sec = divmod(totalSecs, 60)
            hr, minutes = divmod(totalSecs, 60)
            rec.duration= (float(str( "%d:%02d:%02d" % (hr, minutes, sec)).replace(':','.')[:-3]))
            if dates_list:
                rec.date_begin = min(dates_list)
                rec.date_end = max(dates_list)

    def _get_duration(self, date_begin, date_end):
        """ Get the duration value between the 2 given dates. """
        if date_begin and date_end:
            diff = fields.Datetime.from_string(date_end) - fields.Datetime.from_string(date_begin)
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)
                return round(duration, 2)
            return 0.0

    def approve_move_stage(self):
        # call the therapist field onchange function 02-08-22
        self._eve_therapist_id()

        # self._onchangeddd_min_time_end
        # mail has been send while approve the event
        self.approve_value = True
        self.eve_approved_by = self.env.user.id
        self.eve_approved_on = datetime.today()
        template_id = self.env.ref('ppts_custom_event_mgmt.event_approved_mail_template')
        if template_id:
            template_id.send_mail(self.id,force_send=True)
        # mail end

        event_stage_id = self.env['event.stage'].search([('is_published','=',True)],limit=1)
        self.stage_id= event_stage_id.id
        self.is_published=True
        self.event_publish=True
        project_stage_id = self.env['project.task.type'].search([('sequence','=',0)],limit=1)
        self.survey_id.write({'state': 'open'})
        date = self.date_begin.strftime('%Y-%m-%d')
        name = str(self.name + ' (' + date + ')')
        calendar_event = self.env['calendar.event'].create({
            'name': name,
            'start': self.date_begin,
            'start_date': self.date_begin,
            'stop': self.date_end,
            'stop_date': self.date_end,
            'booking_type': 'event',
            'allday': self.allday,
            'name_event': self.id
        })
        self._onchangeddd_min_time_end()
        if self.event_multiple_date == 'oneday':
            a_start = str(self.s_start_date) + ' 00:00:00'
            a_end = str(self.s_start_date) + ' 23:59:59'
        else:
            a_start = str(self.date_begin)
            a_end = str(self.date_end)
        start_date = datetime.strptime(str(a_start), '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(str(a_end), '%Y-%m-%d %H:%M:%S')
        # for i in self.event_ticket_ids:
        #     self.env['product.product'].create({
        #         'name': '',
        #         'product_used': 'event',
        #         'list_price': i.price,
        #         'available_in_pos': True,
        #         'event_ticket': True,
        #         'event_ticket_id': i.id,
        #         'event_id': self.id,
        #     })
        booked_room_ids = self.env['event.meeting.room'].search([('room_id', '=', self.room_id.id),('apt_start_dt', '>=', start_date),('apt_end_dt', '<=', end_date)])
        status_list = []
        if booked_room_ids:
            for room in booked_room_ids:
                now_year = room.apt_start_dt.year
                now_month = room.apt_start_dt.month
                now_date = room.apt_start_dt.day
                now_hr = room.apt_start_dt.hour
                now_min = room.apt_start_dt.minute
                now_sec = 00
                end_now_hr = room.apt_end_dt.hour
                end_now_min = room.apt_end_dt.minute
                date_begin = datetime(now_year, now_month, now_date, now_hr, now_min, now_sec)
                date_begin = date_begin + timedelta(hours=5, minutes=30)
                date_end = datetime(now_year, now_month, now_date, end_now_hr, end_now_min, now_sec)
                date_end = date_end + timedelta(hours=5, minutes=30)
                avail_start = datetime.strptime(str(date_begin), "%Y-%m-%d %H:%M:%S").time()
                avail_end = datetime.strptime(str(date_end), "%Y-%m-%d %H:%M:%S").time()
                start_time_evt = self.hour_time_begin+':'+self.min_time_begin
                end_time_evt = self.hour_time_end+':'+self.min_time_end
                apt_start = datetime.strptime(start_time_evt, '%H:%M').time()
                apt_end = datetime.strptime(end_time_evt, '%H:%M').time()
                res = {}
                if avail_start == apt_start and avail_end == apt_end:
                    self.room_id = False
                    res['warning'] = {'title': _('Warning'), 'message': _('Room Slot not available at this Time.')}
                    return res
                elif avail_start < apt_start < avail_end or avail_start < apt_end < avail_end:
                    self.room_id = False
                    res['warning'] = {'title': _('Warning'), 'message': _('Room Slot not available at this Time.')}
                    return res
                else:
                    if self.class_type.class_room_id.room_maincateg_id:
                        create_room_id = self.env['event.meeting.room'].create({
                            'event_id': self.id,
                            'room_categ_id': self.class_type.class_room_id.room_maincateg_id.id or False,
                            'room_id': self.room_id.id,
                            "name":self.event_type_id.name,
                            "room_max_capacity": 'no_limit',
                            "room_incharge_id": self.class_type.class_room_incharge_id.id or False,
                            "reception_id": self.class_type.reception_id.id or False
                        })
                        self.event_meeting_room_id = create_room_id.id
        else:
            create_room_id = self.env['event.meeting.room'].create({
                'event_id': self.id,
                'room_categ_id': self.class_type.class_room_id.room_maincateg_id.id or False,
                'room_id': self.room_id.id,
                "name":self.event_type_id.name,
                "room_max_capacity": 'no_limit',
                "room_incharge_id": self.class_type.class_room_incharge_id.id or False,
                "reception_id": self.class_type.reception_id.id or False
            })
            self.event_meeting_room_id = create_room_id.id
        if self.reschedule_enable == False:
            checklist = self.env['check.list'].search([('event_id', '=', self.id)])
            self.create_checklist_active = True
            if checklist:
                project = self.env['project.project'].search([('event_id', '=', self.id)])
                if not project:
                    pro_vals = {
                        'name': self.name,
                        'event_id': self.id
                    }
                    project = self.env['project.project'].create(pro_vals)
                    self.project_d_id = project.id
                    project_stage = self.env['project.task.type'].search([('event_stage', '=', True)])
                    if project_stage and project:
                        for pro_stg in project_stage:
                            pro_stg.write({'project_ids': [(4, project.id)]})
                if project:
                    for c_list in checklist:
                        for lines in c_list.checklist_line_id:
                            task = self.env['project.task'].search([('checklist_line_id', '=', lines.id)])
                            if not task:
                                vals = {
                                    'name': lines.checklist_master_id.name,
                                    'user_id': lines.checklist_master_id.responsible.id,
                                    'checklist_line_id': lines.id,
                                    'project_id': project.id,
                                    'date_deadline': lines.end_date,
                                    'start_date': lines.start_date,
                                    'end_date': lines.end_date,
                                    'stage_id': project_stage_id.id
                                }
                                self.project_id = self.env['project.task'].create(vals)
        else:
            checklist = self.env['check.list'].search([('event_id', '=', self.id)])
            if checklist:
                project = self.env['project.project'].search([('event_id', '=', self.id)])

                if project:
                    for c_list in checklist:
                        for lines in c_list.checklist_line_id:
                            task = self.env['project.task'].search([('checklist_line_id', '=', lines.id)])

                            if task:
                                vals = {
                                    'user_id': lines.checklist_master_id.responsible.id,
                                    'checklist_line_id': lines.id,
                                    'project_id': project.id,
                                    'date_deadline': lines.end_date,
                                    'start_date': lines.start_date,
                                    'end_date': lines.end_date,
                                    'stage_id': project_stage_id.id
                                }
                                project_id = task.write(vals)
                            else:
                                vals = {
                                    'name': lines.checklist_master_id.name,
                                    'user_id': lines.checklist_master_id.responsible.id,
                                    'checklist_line_id': lines.id,
                                    'project_id': project.id,
                                    'date_deadline': lines.end_date,
                                    'start_date': lines.start_date,
                                    'end_date': lines.end_date,
                                    'stage_id': project_stage_id.id
                                }
                                project_idd = self.env['project.task'].create(vals)


    def end_move_stage(self):
        event_stage_id = self.env['event.stage'].search([('pipe_end','=',True)],limit=1)
        self.write({'stage_id': event_stage_id.id})
        # use to make readonly cancellation charge 06-09-22
        self.is_ended = True

    def cancel_event_stage(self):
        # to refund the event register amount function 04-07-22
        get_registartion = self.env['event.registration'].search([('event_id','=',self.id)])
        for rec in get_registartion:
            for pos in rec.pos_order_id:
                # if pos order state in New means it will unlink()
                if pos.state == 'draft':
                    pos.unlink()
            if rec.event_payment_status == 'paid':
                event_reg_amount = rec.pos_order_id.amount_paid
                rec.partner_id.CreateCreditPartner(rec.partner_id.id, event_reg_amount)
                rec.event_refund_status = True
        # end

        event_stage_id = self.env['event.stage'].search([('name','=',"Cancelled")],limit=1)
        self.write({'stage_id': event_stage_id.id})
        if self.event_meeting_room_id:
            self.event_meeting_room_id.unlink()
        self.is_published = False
        self.event_publish = False

    def room_smartbtn(self):
        action = self.env.ref('ppts_custom_room_mgmt.room_booking_action_view').read()[0]
        action['domain'] = [('event_id', '=', self.id)]
        return action

    def recurrent(self):
        if self.rrule_type == 'weekly':self.recurrent_week()
        if self.rrule_type == 'monthly':self.recurrent_month()
        if self.rrule_type == 'daily':self.recurrent_day()
        if self.rrule_type == 'yearly':self.recurrent_year()

    def recurrent_year(self):
        lastDayTT = lastDay = self.date_end if self.end_type == 'count' else self.final_date
        user_tz = self.env.user.tz or pytz.utc;local = pytz.timezone(user_tz)
        date = self.date_end.strftime('%Y-%m-%d');name = str(self.name + ' (' +date+ ')')
        if self.allday == False:
            start_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(self.date_begin.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            end_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(lastDayTT.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            start_time = datetime.strptime(start_datetime,'%d-%m-%Y %H:%M:%S');end_time = datetime.strptime(end_datetime,'%d-%m-%Y %H:%M:%S')
            start_time = start_time.strftime('%H:%M');end_time = end_time.strftime('%H:%M');start_time = start_time.replace(":",".");end_time = end_time.replace(":",".")
        else:
            start_time = end_time = 00.00
        use_date = lastDayTT+relativedelta(years=+1)
        name = str(self.name + ' (' +use_date.strftime('%Y-%m-%d')+ ')')
        query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES ("+"'"+str(name)+"'"+", False,"+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+", 'event', 'public', 'busy', True,"+str(self.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
        self.env.cr.execute(query)
        self.create({
            'event_desc':self.event_desc,
            'project_d_id':self.project_d_id.id,
            'checklist_id':self.checklist_id.id,
            'user_id':self.user_id.id,
            'evnt_subcateg':self.evnt_subcateg.id,
            'event_sub_categ_id':self.event_sub_categ_id.id,
            'evnt_maincateg':self.evnt_maincateg.id,
            'evnt_assistant':self.evnt_assistant.id,
            'description':self.description,
            'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),
            'event_id':self.id,
            'eve_therapist_id':self.eve_therapist_id.id,
            'room_id':self.room_id.id,
            'events_type':self.events_type.id,
            'date_begin':use_date,
            'date_end':use_date,
            'address_id':self.address_id.id,'company_id':self.company_id.id})

    def recurrent_day(self):
        lastDayTT = lastDay = self.date_end if self.end_type == 'count' else self.final_date
        user_tz = self.env.user.tz or pytz.utc;local = pytz.timezone(user_tz)
        date = self.date_end.strftime('%Y-%m-%d');name = str(self.name + ' (' +date+ ')')
        if self.allday == False:
            start_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(self.date_begin.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            end_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(lastDayTT.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            start_time = datetime.strptime(start_datetime,'%d-%m-%Y %H:%M:%S');end_time = datetime.strptime(end_datetime,'%d-%m-%Y %H:%M:%S')
            start_time = start_time.strftime('%H:%M');end_time = end_time.strftime('%H:%M');start_time = start_time.replace(":",".");end_time = end_time.replace(":",".")
        else:
            start_time = end_time = 00.00
        if self.end_type == 'count':
            use_date = self.date_end
            for i in range(self.count):
                use_date = use_date+relativedelta(days=+1)
                name = str(self.name + ' (' +use_date.strftime('%Y-%m-%d')+ ')')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES ("+"'"+str(name)+"'"+", False,"+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+", 'event', 'public', 'busy', True,"+str(self.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
                self.env.cr.execute(query)
                self.create({
                    'event_desc':self.event_desc,
                    'project_d_id':self.project_d_id.id,
                    'checklist_id':self.checklist_id.id,
                    'user_id':self.user_id.id,
                    'evnt_subcateg':self.evnt_subcateg.id,
                    'event_sub_categ_id':self.event_sub_categ_id.id,
                    'evnt_maincateg':self.evnt_maincateg.id,
                    'evnt_assistant':self.evnt_assistant.id,
                    'description':self.description,
                    'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),
                    'event_id':self.id,
                    'eve_therapist_id':self.eve_therapist_id.id,
                    'room_id':self.room_id.id,
                    'events_type':self.events_type.id,'date_begin':use_date,'date_end':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})
        else:
            start_date = self.date_end.strftime("%Y-%m-%d")
            end_date = self.final_date
            start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
            def create_events(date):
                name = str(self.name + ' (' +date.strftime('%Y-%m-%d')+ ')')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES ("+"'"+str(name)+"'"+", False,"+"'"+str(date)+"'"+","+"'"+str(date)+"'"+","+"'"+str(date)+"'"+","+"'"+str(date)+"'"+", 'event', 'public', 'busy', True,"+str(self.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
                self.env.cr.execute(query)
                self.create({
                    'event_desc':self.event_desc,
                    'project_d_id':self.project_d_id.id,
                    'checklist_id':self.checklist_id.id,
                    'user_id':self.user_id.id,
                    'evnt_subcateg':self.evnt_subcateg.id,
                    'event_sub_categ_id':self.event_sub_categ_id.id,
                    'evnt_maincateg':self.evnt_maincateg.id,
                    'evnt_assistant':self.evnt_assistant.id,
                    'description':self.description,
                    'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),
                    'event_id':self.id,
                    'eve_therapist_id':self.eve_therapist_id.id,
                    'room_id':self.room_id.id,
                    'events_type':self.events_type.id,'date_begin':use_date,'date_end':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})
            def daterange(start_date, end_date):
                for n in range(int((end_date - start_date).days)):
                    yield start_date + timedelta(n)
            for date in daterange(start_date, end_date):
                last_date = date
                if not date == start_date:
                    create_events(date)
            last_date = last_date+relativedelta(days=+1)
            create_events(last_date)

    def recurrent_month(self):
        import calendar
        use_date = self.date_end + relativedelta(months=+1)
        lastDayTT = lastDay = self.date_end if self.end_type == 'count' else self.final_date
        user_tz = self.env.user.tz or pytz.utc;
        local = pytz.timezone(user_tz)
        date = use_date.strftime('%Y-%m-%d');
        name = str(self.name + ' (' + date + ')')
        year = int(use_date.strftime('%Y'));
        month = int(use_date.strftime('%m'))
        if self.allday == False:
            start_datetime = datetime.strftime(pytz.utc.localize(
                datetime.strptime(self.date_begin.strftime('%Y-%m-%d %H:%M:%S'),
                                  DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d-%m-%Y %H:%M:%S")
            end_datetime = datetime.strftime(pytz.utc.localize(
                datetime.strptime(lastDayTT.strftime('%Y-%m-%d %H:%M:%S'),
                                  DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d-%m-%Y %H:%M:%S")
            start_time = datetime.strptime(start_datetime, '%d-%m-%Y %H:%M:%S');
            end_time = datetime.strptime(end_datetime, '%d-%m-%Y %H:%M:%S')
            start_time = start_time.strftime('%H:%M');
            end_time = end_time.strftime('%H:%M');
            start_time = start_time.replace(":", ".");
            end_time = end_time.replace(":", ".")
        else:
            start_time = end_time = 00.00
        if self.month_by == 'date':
            if self.date_begin.strftime('%d') == use_date.strftime('%d'):
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES (" + "'" + str(
                    name) + "'" + ", False," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + "," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + ", 'event', 'public', 'busy', True," + str(self.id) + "," + str(
                    self.room_id.id) + "," + start_time + "," + end_time + ");"
                self.env.cr.execute(query)
                self.create({
                    'event_desc':self.event_desc,
                    'project_d_id':self.project_d_id.id,
                    'checklist_id':self.checklist_id.id,
                    'user_id':self.user_id.id,
                    'evnt_subcateg':self.evnt_subcateg.id,
                    'event_sub_categ_id':self.event_sub_categ_id.id,
                    'evnt_maincateg':self.evnt_maincateg.id,
                    'evnt_assistant':self.evnt_assistant.id,
                    'description':self.description,
                    'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),
                    'event_id':self.id,
                    'eve_therapist_id':self.eve_therapist_id.id,
                    'room_id':self.room_id.id,
                    'events_type':self.events_type.id,'date_begin':use_date,'date_end':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})
            else:
                raise UserError(_("Next Month Does't have same date!"))
        elif self.month_by == 'day':
            if self.week_list == 'MO': start_day = calendar.MONDAY
            if self.week_list == 'TU': start_day = calendar.TUESDAY
            if self.week_list == 'WE': start_day = calendar.WEDNESDAY
            if self.week_list == 'TH': start_day = calendar.THURSDAY
            if self.week_list == 'FR': start_day = calendar.FRIDAY
            if self.week_list == 'SA': start_day = calendar.SATURDAY
            if self.week_list == 'SU': start_day = calendar.SUNDAY
            dayofweek = 0
            c = calendar.Calendar(firstweekday=start_day)
            monthcal = c.monthdatescalendar(year, month)
            ldates = []
            for tdate in monthcal:
                if tdate[dayofweek].month == month:
                    ldates.append(tdate[dayofweek])
            if self.byday == '1': date = ldates[0]
            if self.byday == '2': date = ldates[1]
            if self.byday == '3': date = ldates[2]
            if self.byday == '4': date = ldates[3]
            if self.byday == '5':
                if len(ldates) > 4:
                    date = ldates[4]
                else:
                    mon_name = str(use_date.strftime('%b'))
                    raise UserError(_("No 5th Week in the Month"))
            query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES (" + "'" + str(
                name) + "'" + ", False," + "'" + str(date) + "'" + "," + "'" + str(date) + "'" + "," + "'" + str(
                date) + "'" + "," + "'" + str(date) + "'" + ", 'event', 'public', 'busy', True," + str(
                self.id) + "," + str(self.room_id.id) + "," + start_time + "," + end_time + ");"
            self.env.cr.execute(query)
            self.create({
                'event_desc':self.event_desc,
                'project_d_id':self.project_d_id.id,
                'checklist_id':self.checklist_id.id,
                'user_id':self.user_id.id,
                'evnt_subcateg':self.evnt_subcateg.id,
                'evnt_maincateg':self.evnt_maincateg.id,
                'evnt_assistant':self.evnt_assistant.id,
                'description':self.description,
                'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),
                'event_id':self.id,
                'eve_therapist_id':self.eve_therapist_id.id,
                'room_id':self.room_id.id,
                'events_type':self.events_type.id,'date_begin':use_date,'date_end':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})

    def recurrent_week(self):
        weekday_en = [];
        req_dates = [];
        err = []
        user_tz = self.env.user.tz or pytz.utc;
        local = pytz.timezone(user_tz)
        if self.mo == True: weekday_en.append('Monday')
        if self.tu == True: weekday_en.append('Tuesday')
        if self.we == True: weekday_en.append('Wednesday')
        if self.th == True: weekday_en.append('Thursday')
        if self.fr == True: weekday_en.append('Friday')
        if self.sa == True: weekday_en.append('Saturday')
        if self.su == True: weekday_en.append('Sunday')
        lastDayTT = lastDay = self.date_end if self.end_type == 'count' else self.final_date
        firstDay = datetime.strptime(self.date_begin.strftime('%d-%B-%Y'), '%d-%B-%Y') + timedelta(days=1)
        lastDay = datetime.strptime(lastDay.strftime('%d-%B-%Y'), '%d-%B-%Y')
        start_datetime = datetime.strftime(pytz.utc.localize(
            datetime.strptime(self.date_end.strftime('%Y-%m-%d %H:%M:%S'),
                              DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strftime(pytz.utc.localize(
            datetime.strptime(lastDayTT.strftime('%Y-%m-%d %H:%M:%S'), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
            local), "%d-%m-%Y %H:%M:%S")
        start_time = datetime.strptime(start_datetime, '%d-%m-%Y %H:%M:%S');
        end_time = datetime.strptime(end_datetime, '%d-%m-%Y %H:%M:%S')
        start_time = start_time.strftime('%H:%M');
        end_time = end_time.strftime('%H:%M');
        start_time = start_time.replace(":", ".");
        end_time = end_time.replace(":", ".")
        for weekDay in weekday_en:
            req_dates.append([firstDay + timedelta(days=x) for x in range((lastDay - firstDay).days + 1) if
                              (firstDay + timedelta(days=x)).weekday() == time.strptime(weekDay, '%A').tm_wday])
        req_dates_all = [val for sublist in req_dates for val in sublist]
        for i in req_dates_all:
            calendar_id = self.env['calendar.event'].search(
                [('booking_type', '=', 'room'), ('room_id', '=', self.room_id.id),
                 ('start_duration', '>=', start_time), ('end_duration', '<=', end_time)])
            if not calendar_id:
                name = str(self.name);
                date = i.strftime('%Y-%m-%d')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES (" + "'" + str(
                    name) + "'" + ", False," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + "," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + ", 'event', 'public', 'busy', True," + str(self.id) + "," + str(
                    self.room_id.id) + "," + start_time + "," + end_time + ");"
                self.env.cr.execute(query)
            self.create({
                'event_desc':self.event_desc,
                'project_d_id':self.project_d_id.id,
                'checklist_id':self.checklist_id.id,
                'user_id':self.user_id.id,
                'evnt_subcateg':self.evnt_subcateg.id,
                'event_sub_categ_id':self.event_sub_categ_id.id,    
                'evnt_maincateg':self.evnt_maincateg.id,
                'evnt_assistant':self.evnt_assistant.id,
                'description':self.description,
                'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),
                'event_id':self.id,
                'eve_therapist_id':self.eve_therapist_id.id,
                'room_id':self.room_id.id,
                'events_type':self.events_type.id,'date_begin':use_date,'date_end':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    type_partner = fields.Selection([('type_existing', 'Existing'), ('type_new', 'New')], string='Type of Customer?',
                                    default='type_existing', required=True)
    extras_partner_id = fields.Many2one('res.partner', string='Customer')
    date_closed = fields.Datetime(string='Attended Date', compute='_compute_date_closed',readonly=True, store=True)


    @api.model
    def create(self, vals):
        res = super(EventRegistration, self).create(vals)
        msg_body = """Creation Date : """ + str(res.create_date.date()) + """ <br/> """ +\
           """Event Name : """ + str(res.event_id.name or 'N/A') + """ <br/> """ +\
           """Event Ticket : """ + str(res.event_ticket_id.name or 'N/A') + """ <br/> """ +\
           """Ticket Price : """ + str(res.ticket_price or 'N/A') + """ <br/> """ +\
           """Register Date : """ + str(res.date_open.date()) +  """ <br/> """ +\
           """Customer Name : """ + str(res.partner_id.name or 'N/A') + """ <br/> """ +\
           """Mobile : """ + str(res.mobile or 'N/A') + """ <br/> """ +\
           """Email: """ + str(res.email or 'N/A') + """ <br/> """ +\
           """Sale Person : """ + str(res.sales_person.name or 'N/A') + """ <br/> """ 
        res.message_post(body=msg_body)
        # create the customer based on new or existing 28-07-22
        if res.partner_id:
            res.partner_id.message_post(body=msg_body)
        else:
            if res.extras_partner_id:
                res.extras_partner_id.message_post(body=msg_body)
        return res

    @api.onchange('type_partner')
    def _onchange_type_partner_domain_relese(self):
        if self.type_partner != 'type_existing':
            self.partner_id = False
            lstt = []
            resp = {'domain': {'extras_partner_id': "[('id', 'not in', False)]"}}
            resp['domain']['extras_partner_id'] = "[('id', 'in', %s)]" % lstt
            return resp

    def action_confirm(self):
        for registration in self:
            if registration.event_id.seats_limited and registration.event_id.seats_max and registration.event_id.seats_available < (1 if registration.state == 'draft' else 0):
                note_id = self.env['event.notification'].search([],limit=1)
                if note_id.attendees_waiting_active_notification_list == True:
                    ctx = dict()
                    for i in note_id.event_attendee_waiting_list:
                        for il in self.env['mailing.contact'].sudo().search([]):
                            if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_waiting_list_mail:
                                ctx.update({
                                    'event':self.event_id.name,
                                    'email':il.email,
                                    'customer_name':self.name,
                                    })
                                for kk in note_id.event_attendee_waiting_list_mail:
                                    kk.sudo().with_context(ctx).send_mail(self.id, force_send=True)
                            if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_waiting_list_whatsapp:
                                self.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_waiting_list_whatsapp.id,pt='mailing_list',apt=self.id)
                    
                    if self.email and note_id.event_attendee_waiting_list_mail:
                        for emp in note_id.event_attendee_waiting_list_mail:
                            ctx.update({
                                'event':self.event_id.name,
                                'email':self.email,
                                'customer_name':self.name,
                                })
                            emp.sudo().with_context(ctx).send_mail(self.id, force_send=True)

                    if self.mobile and note_id.event_attendee_waiting_list_whatsapp:
                        self.event_id.whatsapp_sent(partner_id=self.id,tmpl_id=note_id.event_attendee_waiting_list_whatsapp.id,pt='event_registration',apt=self.id)
                raise ValidationError(_('No more seats available for this event.'))
        res = super(EventRegistration, self).action_confirm()
        if self:
            calendar_mode = self.env['calendar.event']
            calendar_id = calendar_mode.sudo().search([('name_event', '=', self.event_id.id)])
            if calendar_id:
                for cal in calendar_id:
                    cal.partner_ids = [(4, self.partner_id.id)]
            lst = [i.id for i in self.event_id.calendar_id.partner_ids]
            lst.append(self.partner_id.id)
            product_id = self.env['product.product'].sudo().search([('default_code','=','EVENT_REG')],limit=1)
            sale_order_id = self.env['sale.order'].sudo().search([('event_sale_id','=',self.id),('partner_id','=',self.partner_id.id)])
            if self.pos_order_id and self.pos_order_line_id:
                if self.pos_order_id.state == 'paid': 
                    self.payment_status = 'paid'
                if self.pos_order_line_id.service_used_count > 0:
                    self.pos_order_line_id.service_used_count -= 1
                else:
                    raise ValidationError(_("Order doesn't have quantity"))
            else:
                if self.sale_order_id:
                    self.sale_order_id.sudo().action_confirm()
                    self.sale_order_id.order_line[0].invoice_lines[0].move_id.action_post()
                    self.invoice_id = self.sale_order_id.order_line[0].invoice_lines[0].move_id.id
                    self.amount_due = self.sale_order_id.order_line[0].invoice_lines[0].move_id.amount_residual
                    self.amount_total = self.sale_order_id.order_line[0].invoice_lines[0].move_id.amount_total
                    reg_id = self.sudo().search([('event_id','=',self.event_id.id),('partner_id','=',self.partner_id.id)])
                    for i in reg_id:
                        if not i.sale_order_id: i.sale_order_id = self.sale_order_id.id
                else:
                    if sale_order_id:
                        for i in sale_order_id:
                            if not sale_order_id.event_sale_id.sale_order_line_id:
                                self.env['sale.order.line'].sudo().create({
                                                'product_id':self.event_ticket_id.product_id.id,
                                                'event_id':self.event_id.id,
                                                'order_id':i.id,
                                                'event_ticket_id':self.event_ticket_id.id,
                                                'price_unit':float(self.event_ticket_id.price),
                                                })
                    else:
                        lst = []
                        sale_id = self.env['sale.order'].sudo().create({
                            'partner_id':self.partner_id.id,
                            'pricelist_id':1,
                            'event_sale_id':self.event_id.id,
                            'partner_invoice_id':self.partner_id.id,
                            'partner_shipping_id':self.partner_id.id,
                            'state':'sale',
                            'sale_type_for': 'event',
                            })
                        sale_order_id = self.env['sale.order.line'].sudo().create({
                                            'product_id':self.event_ticket_id.product_id.id,
                                            'event_id':self.event_id.id,
                                            'order_id':sale_id.id,
                                            'event_ticket_id':self.event_ticket_id.id,
                                            'price_unit':float(self.event_ticket_id.price),
                                            })

                        if self.apply_coupon_status and self.apply_coupon_flag:
                            coupon= self.env['coupon.coupon'].sudo().search([('code', '=', self.apply_coupon_code)], limit=1)

                            disc_product_id = coupon.program_id.discount_line_product_id.id
                            disc_product_idd = coupon.program_id.discount_line_product_id
                            if not disc_product_idd.sale_ok:
                                disc_product_idd.sudo().write({'sale_ok': True,
                                                               'invoice_policy': 'order',
                                                              })
                            disc_event_price = (coupon.program_id.discount_fixed_amount)*(-1)
                            disc_event_program = coupon.program_id.name
                            disc_sale_order_id = self.env['sale.order.line'].sudo().create({
                                'product_id': disc_product_id,
                                'name': disc_event_program,
                                'event_id': self.event_id.id,
                                'order_id': sale_id.id,
                                'event_ticket_id': self.event_ticket_id.id,
                                'price_unit': float(disc_event_price),
                            })

                            if disc_sale_order_id:
                                coupon.sudo().write({'state': 'used'})

                        self.sale_order_id = sale_id.id
                        self.sale_order_line_id = sale_order_id.id

                    wiz_id = self.env['sale.advance.payment.inv'].sudo().create({"advance_payment_method": "delivered"})
                    wiz_id.with_context(active_ids=sale_id.id).sudo().create_invoices()
                    # sale_id.order_line[0].invoice_lines[0].move_id.sudo().action_post()
                    self.invoice_id = sale_id.order_line[0].invoice_lines[0].move_id.id
                    self.amount_due = sale_id.order_line[0].invoice_lines[0].move_id.amount_residual
                    self.amount_total = sale_id.order_line[0].invoice_lines[0].move_id.amount_total
                    reg_id = self.sudo().search([('event_id','=',self.event_id.id),('partner_id','=',self.partner_id.id)])
                    for i in reg_id:
                        if not i.sale_order_id: 
                            i.sale_order_id = sale_id.id
            note_id = self.env['event.notification'].search([],limit=1)
            if note_id.event_active_notification_attendee_confirmation == True:
                ctx = dict()
                for i in note_id.event_attendee_confirmation_list:
                    for il in self.env['mailing.contact'].sudo().search([]):
                        if il.email and i.id in il.subscription_list_ids.ids and note_id.event_attendee_confirmation_mail:
                            ctx.update({
                                'event':self.event_id.name,
                                'email':il.email,
                                'customer_name':self.name,
                                })
                            for kk in note_id.event_attendee_confirmation_mail:
                                kk.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                        if il.mobile and i.id in il.subscription_list_ids.ids and note_id.event_attendee_confirmation_whatsapp:
                            self.event_id.whatsapp_sent(partner_id=il.id,tmpl_id=note_id.event_attendee_confirmation_whatsapp.id,pt='mailing_list',apt=self.id)
                if self.email and note_id.event_attendee_confirmation_mail:
                    for emp in note_id.event_attendee_confirmation_mail:
                        ctx.update({
                            'event':self.event_id.name,
                            'email':self.email,
                            'customer_name':self.name,
                            })
                        emp.sudo().with_context(ctx).send_mail(self.event_id.id, force_send=True)
                if self.mobile and note_id.event_attendee_confirmation_whatsapp:
                    self.event_id.whatsapp_sent(partner_id=self.id,tmpl_id=note_id.event_attendee_confirmation_whatsapp.id,pt='event_registration',apt=self.id)
            if self.event_id and self.event_id.type_event=='type_online':
                self.state='open'
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    event_ticket = fields.Boolean(string='Ticket')
    event_id = fields.Many2one('event.event',string='Event')
    event_ticket_id = fields.Many2one('event.event.ticket',string='Ticket')
    shipping_handling_charge = fields.Boolean(string="Shipping & Handling Charge")


    @api.constrains('shipping_handling_charge')
    def _validate_shipping_prod(self):
        get_prod = self.env['product.product'].search([('shipping_handling_charge','=',True)])
        if len(get_prod) > 1:
            raise ValidationError(_('It is not advisable to add shipping and handling to more than one product.'))
class EventRejectMaster(models.Model):
    _name = "event.reject.master"

    name = fields.Char(string="Name")

