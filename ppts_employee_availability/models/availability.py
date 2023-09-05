import base64
import requests
from odoo import api, fields, models, _
from dateutil import rrule
from odoo.http import request, Response
import re, pytz
import babel.dates
from odoo import tools
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import get_lang
from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import time
from odoo.tests.common import SavepointCase, HttpSavepointCase, tagged, Form
from lxml import etree
import json

TIME = [('08:00', '08:00'), ('08:15', '08:15'), ('08:30', '08:30'), ('08:45', '08:45'), ('09:00', '09:00'),
        ('09:15', '09:15'), ('09:30', '09:30'), ('09:45', '09:45'), ('10:00', '10:00'), ('10:15', '10:15'),
        ('10:30', '10:30'), ('10:45', '10:45'), ('11:00', '11:00'), ('11:15', '11:15'), ('11:30', '11:30'),
        ('11:45', '11:45'), ('12:00', '12:00'), ('12:15', '12:15'), ('12:30', '12:30'), ('12:45', '12:45'),
        ('13:00', '13:00'), ('13:15', '13:15'), ('13:30', '13:30'), ('13:45', '13:45'), ('14:00', '14:00'),
        ('14:15', '14:15'), ('14:30', '14:30'), ('14:45', '14:45'), ('15:00', '15:00'), ('15:15', '15:15'),
        ('15:30', '15:30'), ('15:45', '15:45'), ('16:00', '16:00'), ('16:15', '16:15'), ('16:30', '16:30'),
        ('16:45', '16:45'), ('17:00', '17:00'), ('17:15', '17:15'), ('17:30', '17:30'), ('17:45', '17:45'),
        ('18:00', '18:00'), ('18:15', '18:15'), ('18:30', '18:30'), ('18:45', '18:45'), ('19:00', '19:00'),
        ('19:15', '19:15'), ('19:30', '19:30'), ('19:45', '19:45'), ('20:00', '20:00'), ('20:15', '20:15'),
        ('20:30', '20:30'), ('20:45', '20:45'), ('21:00', '21:00'), ('21:15', '21:15'), ('21:30', '21:30'),
        ('21:45', '21:45'), ('22:00', '22:00'), ('22:15', '22:15'), ('22:30', '22:30'), ('22:45', '22:45'),
        ('23:00', '23:00'), ('23:15', '23:15'), ('23:30', '23:30'), ('23:45', '23:45')]


class Availability(models.Model):
    _name = 'availability.availability'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Availability'
    _rec_name = 'facilitator'
    _order = 'id desc'


    def _get_company_allowed_domain(self):
        emp_typ = self.env['hr.employee.category'].search([('name', '=', 'Therapist')])
        return [('company_id', '=', self.env.company.id), ('employee_type', 'in', emp_typ.ids)]

    facilitator = fields.Many2one('hr.employee', string='Therapist', domain=_get_company_allowed_domain)
    service_category_ids = fields.One2many('availability.service.line', 'availability_id', string='Services Category')
    tree_service_category_ids = fields.Many2many('availability.service.line',
                                                 'availability_service_line_tree_service_category_ids',
                                                 string='Services Category')
    availabilities_ids = fields.Many2many('availability.availability', 'availability_availability_availabilities_ids', 'av_availabilities_ids', string='Ongoing Availabilities')
    availability = fields.Selection([('available', 'Available'), ('unavailable', 'Unavailable')],
                                    string='Show staff as', default='available')
    location_id = fields.Many2one('res.company', string='Venue', default=lambda self: self.env.company.id)
    date_range = fields.Selection([('ongoing', 'Ongoing'), ('custom', 'Custom Dates')], default='custom', string=" ")
    available_date = fields.Date('Date')  # default=datetime.today()
    start_date = fields.Date()
    end_date = fields.Date()
    state = fields.Selection([('draft', 'Draft'), ('availability_created', 'Availability Created'),
                              ('unavailability_created', 'Unavailability Created')], default='draft')
    start_time = fields.Selection(TIME, required=True)
    end_time = fields.Selection(TIME, required=True)
    privacy = fields.Selection([('0', 'Allow clients to see schedule'), ('1', "Mask staff member's name"),
                                ('2', 'Hide schedule from clients')], default='0')
    event_id = fields.Many2one('event.event', string='Event')
    calendar_classname = fields.Many2one('event.type', 'Class name', related='event_id.event_type_id')
    availabile_type = fields.Selection([('event', 'Event'),
                                        ('appoinment', 'Appoinment'),
                                        ('unavailable', 'Unavailable'),
                                        ('other', 'Others')],
                                       string='Unavailable For', default='unavailable', readonly=True)
    reason = fields.Char("Reason")
    multi_date_selection = fields.Char("Dates")
    cus_start_date = fields.Date("Start Date")
    cus_end_date = fields.Date("End Date")
    appointments_type_id = fields.Many2one('calendar.appointment.type', string='Appointment Type')
    partner_id = fields.Many2one('res.partner', string='Client')
    app_line_id = fields.One2many('availability.availability.line', 'app_id', string="Appointment Dates")
    parent_id = fields.Many2one('availability.availability')
    dayof_the_week = fields.Char(string='Day Of Week', compute='_compute_dayof_the_week')
    date_range_str = fields.Char(string='Date Range', compute='_compute_date_range_str')
    is_customly_created = fields.Boolean(string='Customly Create')
    employee_form = fields.Boolean(string="Created From Employee")

    def unlink(self):
        # using for loop to delete multiple availability entries 30-06-22
        for avail in self:
            availability_ids = self.env['availability.availability'].search([('parent_id','=', avail.id)])
            for rec in availability_ids:
                rec.unlink()
            return super(Availability, self).unlink()

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(Availability, self).default_get(fields_list)

    #     # self._onchange_service_ids_domain()

    #     print(fields_list,'fields_listfields_listfields_listfields_list')

    #     return res

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(Availability, self).fields_view_get(view_id=view_id,
    #                 view_type=view_type, toolbar=toolbar, submenu=submenu)

    #     # if (your_condition):
    #     #     doc = etree.XML(res['arch'])
    #     #     for field in res['fields']:
    #     #         for node in doc.xpath("//field[@name='%s']" % field):
    #     #             node.set("readonly", "1")
    #     #             modifiers = json.loads(node.get("modifiers"))
    #     #             modifiers['readonly'] = True
    #     #             node.set("modifiers", json.dumps(modifiers))
    #     #     res['arch'] = etree.tostring(doc)
    #     print(self._context.get('params'),'-----099089')
    #     if self._context.get('params') and self._context.get('params').get('id'):
    #         print(self._context.get('params').get('id'))
    #     #     self_id = self.env['availability.availability'].browse(int(self._context.get('params').get('id')))
        
        
    #     # print(self_id,'self-----\n')
    #     print('Selffff',self._context.get('params'))
    #     print(res,'-----\n')
    #     print(self,'-----\n')
    #     print(res['fields'],'-----\n\n\n\n\n\n')
    #     return res


    def set_to_draft(self):
        apt_ids = self.env['appointment.appointment'].search([('therapist_id', '=', self.facilitator.id),
                                                              ('booking_date', '=', self.available_date),
                                                              ('state', 'not in', ['no_show', 'cancel'])])
        apt_lst = []
        for rec in apt_ids:
            if rec.time_slot_id:
                avail_start = datetime.strptime(rec.time_slot_id.start_time, '%H:%M').time()
                avail_end = datetime.strptime(rec.time_slot_id.end_time, '%H:%M').time()
                apt_start = datetime.strptime(self.start_time, '%H:%M').time()
                apt_end = datetime.strptime(self.end_time, '%H:%M').time()
                if avail_start <= apt_start <= avail_end or avail_start <= apt_end <= avail_end:
                    apt_lst.append(rec.id)
                if apt_start <= avail_start <= apt_end or apt_start <= avail_end <= apt_end:
                    apt_lst.append(rec.id)
        if apt_lst:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Availability Set To Draft'),
                'res_model': 'availability.setdraft',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                            'default_availability_id': self.id,
                            'default_review_appointment_ids': [(6, 0, apt_lst)],
                            },
                }
        else:
            self.state = 'draft'
            if 'redirect' in self._context and self._context.get('redirect'):
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Availability Availability'),
                    'res_model': 'availability.availability',
                    'res_id': self.id,
                    'target': 'new',
                    'view_mode': 'form',
                    'view_type': 'form',
                }

    def edit_tree(self):
        service_category_type_id = appoinment_type_id = []
        if self.facilitator:
            for i in self.facilitator.pay_rate_ids:
                if i.service_category_type_id.id not in service_category_type_id: 
                    service_category_type_id.append(i.service_category_type_id.id)

        # if self.facilitator and self.service_categ_id:
        #     for i in self.facilitator.pay_rate_ids:
        #         if i.appoinment_type_id.id not in lst and i.service_category_type_id.id in self.service_categ_id.ids: 
        #             lst.append(i.appoinment_type_id.id)

        return {
                'type': 'ir.actions.act_window',
                'name': _('Availability'),
                'res_model': 'availability.availability',
                'res_id': self.id,
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                            'avail_wizard': True,
                            'service_category_type_id': service_category_type_id,
                            # 'appoinment_type_id': appoinment_type_id,
                        },
            }
# to remove the availability
    def action_remove_availability(self):
        apt_ids = self.env['appointment.appointment'].search([('therapist_id', '=', self.facilitator.id),
                                                              ('booking_date', '=', self.available_date),
                                                              ('state', 'not in', ['no_show', 'cancel'])])
        apt_lst = []
        for rec in apt_ids:
            if rec.time_slot_id:
                avail_start = datetime.strptime(rec.time_slot_id.start_time, '%H:%M').time()
                avail_end = datetime.strptime(rec.time_slot_id.end_time, '%H:%M').time()
                apt_start = datetime.strptime(self.start_time, '%H:%M').time()
                apt_end = datetime.strptime(self.end_time, '%H:%M').time()
                if avail_start <= apt_start <= avail_end or avail_start <= apt_end <= avail_end:
                    apt_lst.append(rec.id)
                if apt_start <= avail_start <= apt_end or apt_start <= avail_end <= apt_end:
                    apt_lst.append(rec.id)
        if apt_lst:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Remove Availability'),
                'res_model': 'availability.setdraft',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                            'default_availability_id': self.id,
                            'default_review_appointment_ids': [(6, 0, apt_lst)],
                            },
                }
        else:
            self.unlink()

    @api.depends('available_date', 'cus_start_date', 'cus_end_date')
    def _compute_date_range_str(self):
        for rec in self:
            rec.date_range_str = ''
            if rec.date_range == 'ongoing':
                if rec.available_date:
                    rec.date_range_str = rec.available_date.strftime("%d-%m-%Y")
            else:
                if rec.cus_start_date and rec.cus_end_date:
                    rec.date_range_str = rec.cus_start_date.strftime("%d-%m-%Y") + ' - ' + rec.cus_end_date.strftime("%d-%m-%Y")

    @api.depends('available_date')
    def _compute_dayof_the_week(self):
        for rec in self:
            if rec.date_range == 'ongoing' and rec.available_date:
                rec.dayof_the_week = rec.available_date.strftime("%A")
            else:
                rec.dayof_the_week = ''

    @api.onchange('service_categ_id')
    def _onchange_service_category_ids(self):
        for rec in self:
            if rec.service_categ_id:
                if rec.date_range == 'custom':
                    for i in rec.availabilities_ids:
                        ap_id = self.env['availability.availability'].browse(i._origin.id)
                        ap_id.write({
                            'service_categ_id': [(6, 0, rec.service_categ_id.ids)],
                        })

    def remove_app_line(self):
        if self.app_line_id:
            for i in self.app_line_id:
                i.sudo().unlink()

    @api.onchange('cus_start_date')
    def onchange_cus_start_date(self):
        self.available_date = self.cus_start_date
        self.cus_end_date = self.cus_start_date

    @api.onchange('available_date')
    def onchange_available_date_set_dates(self):
        if self.date_range == 'ongoing':
            self.cus_start_date = self.available_date
            self.cus_end_date = self.available_date

    @api.onchange('start_time', 'end_time')
    def _onchange_appt_time(self):
        if self.end_time and self.start_time:
            avail_start = datetime.strptime(self.start_time, '%H:%M').time()
            avail_end = datetime.strptime(self.end_time, '%H:%M').time()
            if avail_start > avail_end:
                raise UserError(_("Please Enter Valid Time..!!!"))

    @api.model
    def create(self, vals):
        av_idst = self.env['availability.availability'].search([('facilitator', '=', vals['facilitator']),
                                                                ('available_date', '=', vals['available_date']),
                                                                ('date_range', '=', 'ongoing'),
                                                                ('availability', '=', 'available')])
        if vals['date_range'] == 'custom':
            if not vals['app_line_id']: 
                raise UserError(_("You have missed out to click create button for creating availability !!!"))
        if vals['availability'] == 'available':
            for rec in av_idst:
                avail_start = datetime.strptime(rec.start_time, '%H:%M').time()
                avail_end = datetime.strptime(rec.end_time, '%H:%M').time()
                apt_start = datetime.strptime(vals['start_time'], '%H:%M').time()
                apt_end = datetime.strptime(vals['end_time'], '%H:%M').time()
                if avail_start < apt_start < avail_end or avail_start < apt_end < avail_end or avail_start == apt_start or avail_end == apt_end:
                    raise UserError(_("Availability already allotted!!! %s,%s") % (avail_start, avail_end))
                if apt_start < avail_start < apt_end or apt_start < avail_end < apt_end:
                    raise UserError(_("Availability already allotted!!! %s,%s") % (avail_start, avail_end))
            if vals['date_range'] == 'ongoing':
                vals['state'] = 'availability_created'
        else:
            if vals['date_range'] == 'ongoing':
                vals['state'] = 'unavailability_created'
        
        get_appointment_id = self.env['appointment.appointment'].search([('therapist_id', '=', vals['facilitator']),
                                                                ('booking_date', '=', vals['available_date'])])
        avail_start = datetime.strptime(vals['start_time'], '%H:%M').time()
        avail_end = datetime.strptime(vals['end_time'], '%H:%M').time()

        # unavailable validation start 05-07-22

        if vals['availability'] == 'unavailable':
            for rec in get_appointment_id:
                if rec.start_time_str and rec.end_time_str:
                    apt_start = rec.start_time_str
                    apt_end = rec.end_time_str
                    if str(avail_start) and str(avail_end):
                        if apt_start >= str(avail_start)  and apt_end <= str(avail_end):
                            raise UserError(_("Availability already allotted to Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))
                    if apt_start <= str(avail_start):
                        if str(avail_start) <= apt_start and apt_start < str(avail_end):
                            raise UserError(_("Availability already allotted to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))
                        if str(avail_start) <= apt_end and apt_end  < str(avail_end):
                            raise UserError(_("Availability already allotted to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))

                    if str(avail_start) > apt_start:
                        if str(avail_start) >= apt_start and str(avail_start) < apt_end:
                            raise UserError(_("Availability already allocated to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))
        if vals['availability'] == 'available':
            for rec in get_appointment_id:
                if rec.start_time_str and rec.end_time_str:
                    apt_start = rec.start_time_str
                    apt_end = rec.end_time_str
                    if str(avail_start) and str(avail_end):
                        if apt_start >= str(avail_start)  and apt_end <= str(avail_end):
                            raise UserError(_("TAvailability already allotted to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))
                    if apt_start <= str(avail_start):
                        if str(avail_start) <= apt_start and apt_start < str(avail_end):
                            raise UserError(_("Availability already allotted to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))
                        if str(avail_start) <= apt_end and apt_end  < str(avail_end):
                            raise UserError(_("Availability already allotted to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))

                    if str(avail_start) > apt_start:
                        if str(avail_start) >= apt_start and str(avail_start) < apt_end:
                            raise UserError(_("Availability already allotted to another Appointment at this Therapist.\n Appointment Reference - %s \n Appointment Date - %s" % (rec.sequence,rec.booking_date)))

        get_event_id =self.env['multi.date.line'].search([('date_begin','=',vals['available_date']),('event_id.facilitator_evnt_ids','=', vals['facilitator'])])

        if vals['availability'] == 'unavailable' and get_event_id:
            for rec in get_event_id:
                timezone = pytz.timezone(self.env.user.tz or 'UTC')
                event_date_begin = rec.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                event_date_end = rec.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                
                if avail_start and avail_end:
                    if event_date_begin.strftime("%H:%M") >= str(avail_start)  and event_date_end.strftime("%H:%M") <= str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))


                if str(avail_start) <= event_date_begin.strftime("%H:%M"):
                    if str(avail_start) <= event_date_begin.strftime("%H:%M") and event_date_end.strftime("%H:%M") < str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))
                    if str(avail_start) <= event_date_end.strftime("%H:%M") and event_date_end.strftime("%H:%M")  < str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))

                if str(avail_start) > event_date_begin.strftime("%H:%M"):
                    if str(avail_start) >= event_date_begin.strftime("%H:%M") and str(avail_start) < event_date_end.strftime("%H:%M"):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))
        if vals['availability'] == 'available' and get_event_id:
            for rec in get_event_id:
                timezone = pytz.timezone(self.env.user.tz or 'UTC')
                event_date_begin = rec.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                event_date_end = rec.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

                if avail_start and avail_end:
                    if event_date_begin.strftime("%H:%M") >= str(avail_start)  and event_date_end.strftime("%H:%M") <= str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))


                if str(avail_start) <= event_date_begin.strftime("%H:%M"):
                    if str(avail_start) <= event_date_begin.strftime("%H:%M") and event_date_end.strftime("%H:%M") < str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))
                    if str(avail_start) <= event_date_end.strftime("%H:%M") and event_date_end.strftime("%H:%M")  < str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))

                if str(avail_start) > event_date_begin.strftime("%H:%M"):
                    if str(avail_start) >= event_date_begin.strftime("%H:%M") and str(avail_start) < event_date_end.strftime("%H:%M"):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))




        


        if vals['availability'] == 'available' and get_event_id:
            for rec in get_event_id:
                timezone = pytz.timezone(self.env.user.tz or 'UTC')
                event_date_begin = rec.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                event_date_end = rec.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                if avail_start and avail_end:
                    if event_date_begin.strftime("%H:%M") >= str(avail_start) and event_date_end.strftime("%H:%M") <= str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))


                if str(avail_start) <= event_date_begin.strftime("%H:%M"):
                    if str(avail_start) <= event_date_begin.strftime("%H:%M") and event_date_end.strftime("%H:%M") < str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))
                    if str(avail_start) <= event_date_end.strftime("%H:%M") and event_date_end.strftime("%H:%M")  < str(avail_end):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))

                if str(avail_start) > event_date_begin.strftime("%H:%M"):
                    if str(avail_start) >= event_date_begin.strftime("%H:%M") and str(avail_start) < event_date_end.strftime("%H:%M"):
                        raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))

        # Due to string error removed
        # if vals['availability'] == 'available' and get_event_id:
            # for rec in get_event_id:
            #     timezone = pytz.timezone(self.env.user.tz or 'UTC')
            #     event_date_begin = rec.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            #     event_date_end = rec.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            #     if avail_start and avail_end:
            #         if event_date_begin.strftime("%H:%M") >= avail_start  and event_date_end.strftime("%H:%M") <= avail_end:
            #             raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))


            #     if avail_start <= event_date_begin.strftime("%H:%M"):
            #         if avail_start <= event_date_begin.strftime("%H:%M") and event_date_end.strftime("%H:%M") < avail_end:
            #             raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))
            #         if avail_start <= event_date_end.strftime("%H:%M") and event_date_end.strftime("%H:%M")  < avail_end:
            #             raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))

            #     if avail_start > event_date_begin.strftime("%H:%M"):
            #         if avail_start >= event_date_begin.strftime("%H:%M") and avail_start < event_date_end.strftime("%H:%M"):
            #             raise UserError(_("Availability already allotted to another Event at this Therapist.\n Event Name - %s \n Event Reference - %s" % (rec.event_id.name,rec.event_id.event_seq)))


            # unavailable validation ends

        res = super(Availability, self).create(vals)
        if vals['date_range'] == 'custom':
            res.create_availability()
        return res

    def save_redirect(self):
        menu_id = self.env.ref('ppts_employee_availability.availability_tree_view').id
        if 'avail_wizard' in self._context and self._context.get('avail_wizard'):
            return {'type': 'ir.actions.act_window_close'}
        else:
            return {
                "url": "/web?debug=0#&model=availability.availability&view_type=list&cids=&menu_id=" + str(menu_id),
                'target': 'self',
                "type": "ir.actions.act_url"
            }

    def confirm_ongoing(self):
        if self.state == 'draft' and self.date_range == 'ongoing':
            if self.availability == 'available':
                self.state = 'availability_created'
            elif self.availability == 'unavailable':
                self.state = 'unavailability_created'

    def set_wiz(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Appointment Assigned'),
                'res_model': 'availability.unlink',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_av_id': self.id},
                }

    @api.onchange('cus_start_date', 'cus_end_date', 'start_time', 'end_time')
    def _onchange_custom_set_dates(self):
        if self.cus_start_date and self.cus_end_date and self.start_time and self.end_time:
            self.set_dates_in()

    def set_dates_in(self):
        sdate = self.cus_start_date
        edate = self.cus_end_date
        delta = edate - sdate
        line_ids = []
        app_line = []
        for l in self.service_category_ids:
            line_ids.append(l._origin.id)

        def create_line():
            for i in range(delta.days + 1):
                day = sdate + timedelta(days=i)
                setl = day.strftime("%m/%d/%Y")
                print(self.facilitator,"IIIIIIIIIIIIIIIIIIII")
                app_line.append([0, 0, {
                        "facilitator": self.facilitator.id,
                        "date_app": datetime.strptime(setl, "%m/%d/%Y"),
                        "start_time": self.start_time,
                        "end_time": self.end_time,
                        "app_id": self.id,
                        "service_categ_id": self.service_categ_id.ids,
                        "sub_categ_id": self.sub_categ_id.ids,
                    }])
            self.app_line_id = app_line
        if self.app_line_id:
            self.app_line_id = False
            create_line()
        else:
            create_line()
        
    def create_availability(self):
        av_ids = self.env['availability.availability.line'].search([("app_id", "=", self.id)])
        availability_lst = []
        for i in av_ids:
            av_idst = self.env['availability.availability.line'].search(
                [("app_id", "=", self.id), ("date_app", "=", i.date_app), ("start_time", "=", i.start_time),
                 ("end_time", "=", i.end_time)])
            date_id = self.env['date.date'].search([('date', '=', i.date_app.strftime("%Y-%m-%d"))])
            if not date_id:
                self.env['date.date'].create({
                    'name': i.date_app.strftime("%Y-%m-%d"),
                    'date': i.date_app,
                })

            def create_service():
                for k in self.service_category_ids:
                    self.env['availability.service.line'].create({
                        'service_id': k.service_id.id,
                        'availability_id': av_id.id,
                    })
            if len(av_idst) > 1:
                raise UserError(_("Same time already set for this date. Please change the time before continue"))
            else:
                if self.availability == 'available':
                    av_id = self.env['availability.availability'].create({
                        "parent_id": self.id,
                        "facilitator": self.facilitator.id,
                        "date_range": 'ongoing',
                        "availability": 'available',
                        "cus_start_date": i.date_app,
                        "cus_end_date": i.date_app,
                        "available_date": i.date_app,
                        "start_time": i.start_time,
                        "end_time": i.end_time,
                        "is_customly_created": True,
                        "service_categ_id": i.service_categ_id.ids,
                        "sub_categ_id": i.sub_categ_id.ids,
                    })
                    availability_lst.append(av_id.id)
                    create_service()
                    self.state = 'availability_created'
                else:
                    al_id = self.env['availability.availability'].create({
                        "parent_id": self.id,
                        "facilitator": self.facilitator.id,
                        "date_range": 'ongoing',
                        "availability": 'unavailable',
                        "reason": self.reason,
                        "cus_start_date": i.date_app,
                        "cus_end_date": i.date_app,
                        "available_date": i.date_app,
                        "start_time": i.start_time,
                        "end_time": i.end_time,
                        "is_customly_created": True,
                        "service_categ_id": self.service_categ_id.ids,
                        "sub_categ_id": self.sub_categ_id.ids,
                    })
                    availability_lst.append(al_id.id)
                    create_service()
                    self.state = 'unavailability_created'
        self.availabilities_ids = availability_lst

    @api.onchange('available_date')
    def onchange_available_date(self):
        if self.available_date:
            if self.available_date < date.today():
                self.available_date = date.today()
                self.cus_start_date = False
                self.cus_end_date = False
                return {'warning': {
                    'title': _("Warning"),
                    'message': "Please select a date equal/or greater tha n the current date"
                }}

    @api.onchange('end_date')
    def _onchange_available_dates(self):
        if self.start_date and self.end_date:
            self.available_dates = ''
            sdate = self.start_date  # start date
            edate = self.end_date  # end date
            delta = edate - sdate  # as timedelta
            for i in range(delta.days + 1):
                day = sdate + timedelta(days=i)
                day = day.strftime("%Y-%m-%d")
                self.available_dates += day + ','
            self.available_dates = self.available_dates[:-1]

    def action_view_avail(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Dates',
            'view_mode': 'tree,form',
            'res_model': 'availability.availability',
            'domain': [('parent_id', '=', self.id)],
        }


class AvailabilityServiceLine(models.Model):
    _name = 'availability.service.line'
    _description = 'Availability Service Line'

    availability_id = fields.Many2one('availability.availability', string="Availability")
    availability_line_id = fields.Many2one('availability.availability.line', string="Availability")
    active_id = fields.Boolean('Inactive')


class AvailabilityLine(models.Model):
    _name = 'availability.availability.line'
    _description = 'Availability Line'

    facilitator = fields.Many2one('hr.employee', string='Facilitator')
    date_app = fields.Date("Date", required=True)
    start_time = fields.Selection(TIME, "Start time", required=True)
    end_time = fields.Selection(TIME, "End time", required=True)
    app_id = fields.Many2one('availability.availability', string='App id')
    service_category_ids = fields.One2many('availability.service.line', 'availability_line_id',
                                           string='Services Category')
    is_services = fields.Boolean(string="Edit Services")
