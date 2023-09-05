from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

hour_time = [('01', "01"),('02', "02"),('03', "03"),('04', "04"),('05', "05"),('06', "06"),('07', "07"),('08', "08"),('09', "09"),('10', "10"),('11', "11"),('12', "12"),('13', "13"),('14', "14"),('15', "15"),('16', "16"),('17', "17"),('18', "18"),('19', "19"),('20', "20"),('21', "21"),('22', "22"),('23', "23")];
min_time=[('00', "00"),
          ('05', "05"),
          ('10', "10"),
          ('15', "15"),
          ('20', "20"),
          ('25', "25"),
          ('30', "30"),
          ('35', "35"),
          ('40', "40"),
          ('45', "45"),
          ('50', "50"),
          ('55', "55")];

class CustomEventMultiDate(models.Model):
    _inherit = 'event.event'

    date_begin = fields.Datetime(string='Start Date', required=False)
    date_end = fields.Datetime(string='End Date', required=False)
    event_multiple_date=fields.Selection([('oneday','Single Day'),('multiday','Multiple Days')],
                                         default='oneday',string='Event Days',help='Defines Event is planned for Single / Multiple Days. '
                                                                                   'Based on Selection user should select Date shown below')
    s_start_date = fields.Date('Date')
    multi_date_select = fields.Char('Select Date')
    hour_time_begin = fields.Selection(hour_time, string='Hour', copy=False, help='Event Start Hour(s)')
    min_time_begin = fields.Selection(min_time, string='Minute', copy=False, help='Event Start Minute(s)',default='00')
    time_begin = fields.Float(string='Start Time')
    hour_time_end = fields.Selection(hour_time, string='Hours', copy=False,help='Event End Hour(s)')
    min_time_end = fields.Selection(min_time, string='Minutes', copy=False, help='Event End Minute(s)',default='00')
    time_end = fields.Float(string='End Time')
    is_multi_date=fields.Boolean(string='Multi Date Lines',default=False)
    multi_date_line_ids=fields.One2many('multi.date.line','event_id',string='Date Lines')

    @api.onchange('event_multiple_date','min_time_end', 'hour_time_end', 'hour_time_begin', 'min_time_begin','s_start_date')
    def _onchange_multi_date(self):
        if self.multi_date_line_ids and self.event_multiple_date != 'multiday':
            self.multi_date_line_ids = False
        if self.event_multiple_date == 'multiday':
            self.is_multi_date=True
        else:
            self.is_multi_date = False

    # update multidate functionality to update the values if open the wizard 10-08-22

    def action_update_multidate(self):
        if self.multi_date_line_ids:
            start_date = self.multi_date_line_ids[0].date_begin
            end_date = self.multi_date_line_ids[-1].date_end
            hour_time_begin = self.multi_date_line_ids[0].hour_time_begin
            hour_time_end = self.multi_date_line_ids[-1].hour_time_end
            min_time_begin = self.multi_date_line_ids[0].min_time_begin
            min_time_end = self.multi_date_line_ids[-1].min_time_end
                
            return {
                'name': _('Update Multiple Dates'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'multi.date.wizard',
                'views': [(False, 'form')],
                'view_id': 'view_multidate_wizard_form',
                'target': 'new',
                'context': {'default_event_wiz_id': self.id,'default_facilitator_evnt_ids':self.facilitator_evnt_ids.ids,'default_room_id':self.room_id.id,'default_date_begin':start_date,'default_date_end':end_date,'default_hour_time_begin':hour_time_begin,
                'default_hour_time_end':hour_time_end,'default_min_time_begin':min_time_begin,'default_min_time_end':min_time_end}
            }

# used for multi date wizard validation for room 10-08-22
    def multidate_room_validation(self):
        multi_date= False
        for each_date in self.multi_date_line_ids:
            room_exists =self.env['multi.date.line'].search([('event_id.room_id' , '=',self.room_id.id),('event_id','!=', False),('event_id.id','!=',self._origin.id),
                                                            ('m_date_begin', '<=', each_date.m_date_begin), ('m_date_end', '>=', each_date.m_date_end)])
            if room_exists:
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

# used for multi date wizard validation for therapist 10-08-22

    def therapist_multidate_room_validation(self):
        if self.facilitator_evnt_ids:
            for each_date in self.multi_date_line_ids:
                therapist_exists =self.env['multi.date.line'].search([('event_id.facilitator_evnt_ids' , 'in',self.facilitator_evnt_ids.ids),('event_id','!=', False),('event_id.id','!=',self._origin.id),
                                                                ('m_date_begin', '<=', each_date.m_date_begin), ('m_date_end', '>=', each_date.m_date_end)])
                if therapist_exists: 
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



    def create_multi_date_line(self):
        if self.s_start_date and self.hour_time_begin and self.min_time_begin and self.min_time_end and self.hour_time_end:
            dubai_zone_begin = (self.date_begin - timedelta(hours=1, minutes=30))
            dubai_zone_end = (self.date_end - timedelta(hours=1, minutes=30))
            vals={
                    'date_begin':self.s_start_date,
                    'hour_time_begin':self.hour_time_begin,
                    'min_time_begin':self.min_time_begin,
                    'm_date_begin':dubai_zone_begin if self.date_tz == 'Asia/Dubai' else self.date_begin,
                    'date_end':self.s_start_date,
                    'hour_time_end':self.hour_time_end,
                    'min_time_end':self.min_time_end,
                    'm_date_end':dubai_zone_end if self.date_tz == 'Asia/Dubai' else self.date_end,
                    'duration':self.duration,
                    'event_id':self.id
                }

            self.multi_date_line_ids.create(vals)
# Added duration and stage_id to calculate the event date 03-08-22
    @api.onchange('min_time_end', 'hour_time_end', 'hour_time_begin', 'min_time_begin','s_start_date')
    def _onchangeddd_min_time_end(self):
        if self.s_start_date and self.hour_time_begin and self.min_time_begin and self.hour_time_end and self.min_time_end:
            now_year=self.s_start_date.year
            now_month=self.s_start_date.month
            now_date=self.s_start_date.day
            now_hr= int(self.hour_time_begin)
            now_min= int(self.min_time_begin)
            now_sec=00
            now_hr_e = int(self.hour_time_end)
            now_min_e = int(self.min_time_end)
            local_tz = pytz.timezone(self.date_tz)
            date_begin = local_tz.localize(datetime(now_year, now_month, now_date, now_hr, now_min, now_sec)).astimezone(
            pytz.utc).replace(tzinfo=None)
            date_end = local_tz.localize(datetime(now_year, now_month, now_date, now_hr_e, now_min_e, now_sec)).astimezone(
            pytz.utc).replace(tzinfo=None)
            self.date_begin = date_begin
            self.date_end = date_end
            # used to get the event date and time 04-08-22
            if not self.event_publish:
                self.create_multi_date_line()

            # self.action_compute_get_date()

    def multi_date_wiz(self):
        return {
            'name': _('Add Multiple Dates'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'multi.date.wizard',
            'views': [(False, 'form')],
            'view_id': 'view_multidate_wizard_form',
            'target': 'new',
            'context': {'default_event_wiz_id': self.id,'default_company_id':self.company_id.id}
        }

    def update_multidate_fields(self):
        dates_list = []
        tot_dur=0.0
        for lst_ids in self.multi_date_line_ids:
            dates_list.append(lst_ids.m_date_begin)
            dates_list.append(lst_ids.m_date_end)
            dates_list = list(filter(bool,dates_list))
            tot_dur = tot_dur + lst_ids.duration
        min_date = min(dates_list)
        max_date = max(dates_list)        
        self.update({'duration': tot_dur})
        self.date_begin = min_date
        self.date_end = max_date

class EventMultiDateLine(models.Model):
    _name = 'multi.date.line'
    _description="EventMultiDateLine"

    event_id=fields.Many2one('event.event',string="Event")
    name = fields.Char(string="Event name" ,related='event_id.name')
    date_begin = fields.Date(string='Start Date')
    hour_time_begin = fields.Selection(hour_time, string='Hours', copy=False)
    min_time_begin = fields.Selection(min_time, string='Minutes', copy=False)
    m_date_begin = fields.Datetime(string='Start Date Time')
    date_end = fields.Date(string='End Date')
    hour_time_end = fields.Selection(hour_time, string='Hours', copy=False)
    min_time_end = fields.Selection(min_time, string='Minutes', copy=False)
    m_date_end = fields.Datetime(string='End Date Time')
    duration = fields.Float(string='Duration',compute='_compute_duration',store=True, copy=False)

    @api.onchange('min_time_end', 'hour_time_end', 'hour_time_begin', 'min_time_begin', 'date_begin')
    def _onchang_event_dates(self):
        if self.date_begin and self.hour_time_begin and self.min_time_begin:
            now_year = self.date_begin.year
            now_month = self.date_begin.month
            now_date = self.date_begin.day
            now_hr = int(self.hour_time_begin)
            now_min = int(self.min_time_begin)
            now_sec = 00
            local_tz = pytz.timezone(self.event_id.date_tz)
            date_begin = local_tz.localize(datetime(now_year, now_month, now_date, now_hr, now_min, now_sec)).astimezone(
                pytz.utc).replace(tzinfo=None)
            self.m_date_begin = date_begin
        if self.date_end and self.hour_time_end and self.min_time_end:
            now_hr_e = int(self.hour_time_end)
            now_min_e = int(self.min_time_end)
            date_end = local_tz.localize(datetime(now_year, now_month, now_date, now_hr_e, now_min_e, now_sec)).astimezone(
                pytz.utc).replace(tzinfo=None)
            self.m_date_end = date_end
        if self.m_date_end and self.m_date_begin:
            self.event_id.update_multidate_fields()

    @api.depends('m_date_end', 'm_date_begin')
    def _compute_duration(self):
        for rec in self:
            if rec.m_date_end and rec.m_date_begin:
                if rec.m_date_end<rec.m_date_begin:
                    raise UserError('Please Select correct Date & Time for Event!')
                else:
                    duration = (rec.m_date_end-rec.m_date_begin)
                    start_time = datetime.strptime(str(duration), "%H:%M:%S")
                    start_time = start_time.strftime("%H.%M")
                    rec.duration = float(start_time)
