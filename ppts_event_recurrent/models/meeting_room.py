from odoo import api, fields, models, _
from dateutil import rrule
import re
import pytz
import babel.dates
from odoo import tools
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.tools.misc import get_lang
from num2words import num2words
from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import time,inflect
 
RECURRSION = [('norepeat',"Doesn't repeat"),('daily','Daily')];WEEKLY = [];p = inflect.engine()
TODAY = datetime.now();r_MONTH = []
DAY = TODAY.strftime("%A");DAY_NUMBER = int(TODAY.strftime("%w"))
RECURRSION.append(("week","Weekly on "+DAY))
TODAY_D = date.today();MONTH_D = TODAY.strftime("%B %d");DAY_D = TODAY.strftime("%d");MONTH_r = int(TODAY.strftime("%m")) 
YEAR = TODAY_D.year;MONTH = TODAY_D.month
date_object = date(YEAR, MONTH, 1)
date_object += timedelta(days=DAY_NUMBER-date_object.isoweekday())
 
while date_object.year == YEAR:
    if date_object.month == MONTH:WEEKLY.append(date_object)
    date_object += timedelta(days=7)
# if TODAY_D in WEEKLY:
WEEKLY_INT = 1
# WEEKLY.index(TODAY_D)
RECURRSION.append(("monthly","Monthly on the "+p.ordinal(WEEKLY_INT+1)+' '+DAY));RECURRSION.append(("annually","Annually on "+MONTH_D));RECURRSION.append(('custom','Custom...'))
r_MONTH.append(("monthly_word","Monthly on the "+p.ordinal(WEEKLY_INT+1)+' '+DAY));r_MONTH.append(("monthly_date","Monthly on day "+DAY_D))
TIME_T = [('12:00AM','12:00AM'),('12:05AM','12:05AM'),('12:10AM','12:10AM'),('12:15AM','12:15AM'),('12:20AM','12:20AM'),('12:25AM','12:25AM'),('12:30AM','12:30AM'),('12:35AM','12:35AM'),('12:40AM','12:40AM'),('12:45AM','12:45AM'),('12:50AM','12:50AM'),('12:55AM','12:55AM'),('01:00AM','01:00AM'),('01:05AM','01:05AM'),('01:10AM','01:10AM'),('01:15AM','01:15AM'),('01:20AM','01:20AM'),('01:25AM','01:25AM'),('01:30AM','01:30AM'),('01:35AM','01:35AM'),('01:40AM','01:40AM'),('01:45AM','01:45AM'),('01:50AM','01:50AM'),('01:55AM','01:55AM'),('02:00AM','02:00AM'),('02:05AM','02:05AM'),('02:10AM','02:10AM'),('02:15AM','02:15AM'),('02:20AM','02:20AM'),('02:25AM','02:25AM'),('02:30AM','02:30AM'),('02:35AM','02:35AM'),('02:40AM','02:40AM'),('02:45AM','02:45AM'),('02:50AM','02:50AM'),('02:55AM','02:55AM'),('03:00AM','03:00AM'),('03:05AM','03:05AM'),('03:10AM','03:10AM'),('03:15AM','03:15AM'),('03:20AM','03:20AM'),('03:25AM','03:25AM'),('03:30AM','03:30AM'),('03:35AM','03:35AM'),('03:40AM','03:40AM'),('03:45AM','03:45AM'),('03:50AM','03:50AM'),('03:55AM','03:55AM'),('04:00AM','04:00AM'),('04:05AM','04:05AM'),('04:10AM','04:10AM'),('04:15AM','04:15AM'),('04:20AM','04:20AM'),('04:25AM','04:25AM'),('04:30AM','04:30AM'),('04:35AM','04:35AM'),('04:40AM','04:40AM'),('04:45AM','04:45AM'),('04:50AM','04:50AM'),('04:55AM','04:55AM'),('05:00AM','05:00AM'),('05:05AM','05:05AM'),('05:10AM','05:10AM'),('05:15AM','05:15AM'),('05:20AM','05:20AM'),('05:25AM','05:25AM'),('05:30AM','05:30AM'),('05:35AM','05:35AM'),('05:40AM','05:40AM'),('05:45AM','05:45AM'),('05:50AM','05:50AM'),('05:55AM','05:55AM'),('06:00AM','06:00AM'),('06:05AM','06:05AM'),('06:10AM','06:10AM'),('06:15AM','06:15AM'),('06:20AM','06:20AM'),('06:25AM','06:25AM'),('06:30AM','06:30AM'),('06:35AM','06:35AM'),('06:40AM','06:40AM'),('06:45AM','06:45AM'),('06:50AM','06:50AM'),('06:55AM','06:55AM'),('07:00AM','07:00AM'),('07:05AM','07:05AM'),('07:10AM','07:10AM'),('07:15AM','07:15AM'),('07:20AM','07:20AM'),('07:25AM','07:25AM'),('07:30AM','07:30AM'),('07:35AM','07:35AM'),('07:40AM','07:40AM'),('07:45AM','07:45AM'),('07:50AM','07:50AM'),('07:55AM','07:55AM'),('08:00AM','08:00AM'),('08:05AM','08:05AM'),('08:10AM','08:10AM'),('08:15AM','08:15AM'),('08:20AM','08:20AM'),('08:25AM','08:25AM'),('08:30AM','08:30AM'),('08:35AM','08:35AM'),('08:40AM','08:40AM'),('08:45AM','08:45AM'),('08:50AM','08:50AM'),('08:55AM','08:55AM'),('09:00AM','09:00AM'),('09:05AM','09:05AM'),('09:10AM','09:10AM'),('09:15AM','09:15AM'),('09:20AM','09:20AM'),('09:25AM','09:25AM'),('09:30AM','09:30AM'),('09:35AM','09:35AM'),('09:40AM','09:40AM'),('09:45AM','09:45AM'),('09:50AM','09:50AM'),('09:55AM','09:55AM'),('10:00AM','10:00AM'),('10:05AM','10:05AM'),('10:10AM','10:10AM'),('10:15AM','10:15AM'),('10:20AM','10:20AM'),('10:25AM','10:25AM'),('10:30AM','10:30AM'),('10:35AM','10:35AM'),('10:40AM','10:40AM'),('10:45AM','10:45AM'),('10:50AM','10:50AM'),('10:55AM','10:55AM'),('11:00AM','11:00AM'),('11:05AM','11:05AM'),('11:10AM','11:10AM'),('11:15AM','11:15AM'),('11:20AM','11:20AM'),('11:25AM','11:25AM'),('11:30AM','11:30AM'),('11:35AM','11:35AM'),('11:40AM','11:40AM'),('11:45AM','11:45AM'),('11:50AM','11:50AM'),('11:55AM','11:55AM'),('12:00PM','12:00PM'),('12:05PM','12:05PM'),('12:10PM','12:10PM'),('12:15PM','12:15PM'),('12:20PM','12:20PM'),('12:25PM','12:25PM'),('12:30PM','12:30PM'),('12:35PM','12:35PM'),('12:40PM','12:40PM'),('12:45PM','12:45PM'),('12:50PM','12:50PM'),('12:55PM','12:55PM'),('01:00PM','01:00PM'),('01:05PM','01:05PM'),('01:10PM','01:10PM'),('01:15PM','01:15PM'),('01:20PM','01:20PM'),('01:25PM','01:25PM'),('01:30PM','01:30PM'),('01:35PM','01:35PM'),('01:40PM','01:40PM'),('01:45PM','01:45PM'),('01:50PM','01:50PM'),('01:55PM','01:55PM'),('02:00PM','02:00PM'),('02:05PM','02:05PM'),('02:10PM','02:10PM'),('02:15PM','02:15PM'),('02:20PM','02:20PM'),('02:25PM','02:25PM'),('02:30PM','02:30PM'),('02:35PM','02:35PM'),('02:40PM','02:40PM'),('02:45PM','02:45PM'),('02:50PM','02:50PM'),('02:55PM','02:55PM'),('03:00PM','03:00PM'),('03:05PM','03:05PM'),('03:10PM','03:10PM'),('03:15PM','03:15PM'),('03:20PM','03:20PM'),('03:25PM','03:25PM'),('03:30PM','03:30PM'),('03:35PM','03:35PM'),('03:40PM','03:40PM'),('03:45PM','03:45PM'),('03:50PM','03:50PM'),('03:55PM','03:55PM'),('04:00PM','04:00PM'),('04:05PM','04:05PM'),('04:10PM','04:10PM'),('04:15PM','04:15PM'),('04:20PM','04:20PM'),('04:25PM','04:25PM'),('04:30PM','04:30PM'),('04:35PM','04:35PM'),('04:40PM','04:40PM'),('04:45PM','04:45PM'),('04:50PM','04:50PM'),('04:55PM','04:55PM'),('05:00PM','05:00PM'),('05:05PM','05:05PM'),('05:10PM','05:10PM'),('05:15PM','05:15PM'),('05:20PM','05:20PM'),('05:25PM','05:25PM'),('05:30PM','05:30PM'),('05:35PM','05:35PM'),('05:40PM','05:40PM'),('05:45PM','05:45PM'),('05:50PM','05:50PM'),('05:55PM','05:55PM'),('06:00PM','06:00PM'),('06:05PM','06:05PM'),('06:10PM','06:10PM'),('06:15PM','06:15PM'),('06:20PM','06:20PM'),('06:25PM','06:25PM'),('06:30PM','06:30PM'),('06:35PM','06:35PM'),('06:40PM','06:40PM'),('06:45PM','06:45PM'),('06:50PM','06:50PM'),('06:55PM','06:55PM'),('07:00PM','07:00PM'),('07:05PM','07:05PM'),('07:10PM','07:10PM'),('07:15PM','07:15PM'),('07:20PM','07:20PM'),('07:25PM','07:25PM'),('07:30PM','07:30PM'),('07:35PM','07:35PM'),('07:40PM','07:40PM'),('07:45PM','07:45PM'),('07:50PM','07:50PM'),('07:55PM','07:55PM'),('08:00PM','08:00PM'),('08:05PM','08:05PM'),('08:10PM','08:10PM'),('08:15PM','08:15PM'),('08:20PM','08:20PM'),('08:25PM','08:25PM'),('08:30PM','08:30PM'),('08:35PM','08:35PM'),('08:40PM','08:40PM'),('08:45PM','08:45PM'),('08:50PM','08:50PM'),('08:55PM','08:55PM'),('09:00PM','09:00PM'),('09:05PM','09:05PM'),('09:10PM','09:10PM'),('09:15PM','09:15PM'),('09:20PM','09:20PM'),('09:25PM','09:25PM'),('09:30PM','09:30PM'),('09:35PM','09:35PM'),('09:40PM','09:40PM'),('09:45PM','09:45PM'),('09:50PM','09:50PM'),('09:55PM','09:55PM'),('10:00PM','10:00PM'),('10:05PM','10:05PM'),('10:10PM','10:10PM'),('10:15PM','10:15PM'),('10:20PM','10:20PM'),('10:25PM','10:25PM'),('10:30PM','10:30PM'),('10:35PM','10:35PM'),('10:40PM','10:40PM'),('10:45PM','10:45PM'),('10:50PM','10:50PM'),('10:55PM','10:55PM'),('11:00PM','11:00PM'),('11:05PM','11:05PM'),('11:10PM','11:10PM'),('11:15PM','11:15PM'),('11:20PM','11:20PM'),('11:25PM','11:25PM'),('11:30PM','11:30PM'),('11:35PM','11:35PM'),('11:40PM','11:40PM'),('11:45PM','11:45PM'),('11:50PM','11:50PM'),('11:55PM','11:55PM')]

# class CalendarEvent(models.Model):
#     _inherit = 'calendar.event'
#
#     r_start_time = fields.Selection(TIME_T,string='Start Time',default='10:00AM')
#     r_end_time = fields.Selection(TIME_T,string='End Time',default='11:00AM')

class CustomMeetingRoomRecur(models.Model):
    _inherit = 'event.meeting.room'

    r_start_date = fields.Date('Start Date',store=True)
    r_end_date = fields.Date('End Date',store=True)

    r_start_time = fields.Selection(TIME_T,string='Start Time',default='10:00AM',store=True)
    r_end_time = fields.Selection(TIME_T,string='End Time',default='11:00AM',store=True)

    r_allday = fields.Boolean('All day')
    r_recurrsion_type = fields.Selection(RECURRSION,string='Recurrsion Type',default="norepeat")

    r_repeat_count = fields.Integer('Repeat every',store=True,default=1)
    r_repeat_type = fields.Selection([('day','Day'),('week','Week'),('month','Month'),('year','Year')],default="day",string="Type")

    r_repeat_end = fields.Selection([('enddate','End Date'),('count','Count')],default="enddate",string="End")
    r_repeat_enddate = fields.Date('End Date')
    r_repeat_endcount = fields.Integer('Occurrences',store=True,default=1)

    MO = fields.Boolean('Monday')
    TU = fields.Boolean('Tuesday')
    WE = fields.Boolean('Wednesday')
    TH = fields.Boolean('Thursday')
    FR = fields.Boolean('Friday')
    SA = fields.Boolean('Saturday')
    SU = fields.Boolean('Sunday')

    r_repeat_type_month = fields.Selection(r_MONTH,string="Repeat Type",default="monthly_word")

    @api.onchange('r_repeat_count')
    def _onchange_r_repeat_endcount(self):
        if self.r_repeat_count == 0:
            self.r_repeat_count = 1

    @api.onchange('r_repeat_endcount')
    def _onchange_r_repeat_endcount_date(self):
        if self.r_repeat_endcount == 0:
            self.r_repeat_endcount = 1

    @api.onchange('event_id')
    def _onchange_date_event(self):

        if self.event_id.date_begin and self.event_id.date_end:
            user_tz = self.event_id.date_tz
            local = pytz.timezone(user_tz)

            self.r_start_date = self.event_id.date_begin;self.r_end_date = self.event_id.date_end
            start_hr = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_begin.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%I:%M%p")
            end_hr = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%I:%M%p")
            self.r_start_time = start_hr
            self.r_end_time = end_hr

    def eventRecurrsion(self, date):
        def convert24(str1): 
            if str1[-2:] == "AM" and str1[:2] == "12": 
                return "00" + str1[2:-2] 
            elif str1[-2:] == "AM": 
                return str1[:-2] 
            elif str1[-2:] == "PM" and str1[:2] == "12": 
                return str1[:-2] 
            else: 
                return str(int(str1[:2]) + 12) + str1[2:8]        

        user_tz = self.event_id.date_tz;week_days = [];local = pytz.timezone(user_tz)

        end_date_Y = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y");end_date_m = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%m");end_date_d = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d")
        end_date = datetime(int(end_date_Y),int(end_date_m),int(end_date_d))
        end_date_oneplus = end_date+timedelta(days=1)
        CalendarEvent = self.env['calendar.event']
        reg_id = self.env['event.registration'].search([('event_id','=',self.id)])
        domain = [('name_event','=',self.id),('start','=',end_date_oneplus)]
        lst = [i.partner_id.id for i in reg_id if i.partner_id.id]
        if self.r_allday == False:
            start_time = datetime.strptime(str(self.r_start_time), "%I:%M%p")
            end_time = datetime.strptime(str(self.r_end_time), "%I:%M%p")

            light_start = start_time.strftime("%p")
            start_time = start_time.strftime("%I.%M")

            light_end = end_time.strftime("%p")
            end_time = end_time.strftime("%I.%M")
            domain.append(('start_duration','>=',start_time))
            domain.append(('end_duration','<=',end_time))
            domain.append(('booking_type','=','room'))
        else:
            start_time = end_time = 0.0
            light_start = light_end = ''

        st_tt = self.event_id.date_begin.strftime('%I:%M:%S %p')
        et_tt = self.event_id.date_end.strftime("%I:%M:%S %p")

        def date_to_datetime(dt, time_st):
            tt = time_st.split(':')
            date_ct = datetime(dt.year, dt.month, dt.day, int(tt[0]), int(tt[1]), int(tt[2]))
            return date_ct

        dt = date.strftime('%Y-%m-%d')
        dt = datetime.strptime(date.strftime('%Y-%m-%d'), "%Y-%m-%d")


        start_datetime_re = date_to_datetime(dt, convert24(st_tt))
        end_datetime_re = date_to_datetime(dt, convert24(et_tt))
        calendar_id = CalendarEvent.search(domain)

        if calendar_id==9:
            raise UserError(_("Room Booked For Same Date and Time"))
        else:
            CalendarEvent.create({
                'name': str(self.name + ' (' +date.strftime('%Y-%m-%d')+ ')'),
                'start' : date,
                'stop' : date,
                'start_date' : date,
                'stop_date' : date,
                'duration' : self.duration,
                # 'description': self.event_desc,
                'name_facilitator': self.therapist_id.id,
                'booking_type':'room',
                'room_id':self.room_id.id,
                'allday':self.r_allday,
                'start_duration':float(start_time),
                'end_duration':float(end_time),
                'du_start_light':light_start,
                'du_end_light':light_end,
                'partner_ids': [(6, 0, lst)],
                'show_as':'busy',
                'name_event': self.event_id.id,
                })

        self.create({
            'name':self.name,
            'event_id':self.event_id.id,
            'therapist_id': self.therapist_id.id,
            'room_categ_id': self.room_categ_id.id,
            'room_id': self.room_id.id,
            'event_location_id': self.room_id.id,
            'room_incharge_id': self.room_incharge_id.id,
            'max_seats': self.max_seats,
            'room_max_capacity': 'no_limit',
            'event_start_dt': start_datetime_re,
            'event_end_dt': end_datetime_re,
            })

    def recurrsion(self):
        from dateutil.rrule import rrule, MONTHLY, DAILY, WEEKLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
        from datetime import date, timedelta

        user_tz = self.event_id.date_tz;week_days = [];local = pytz.timezone(user_tz);now = datetime.now()
        if now.strftime("%A") == "Sunday":day_char = SU
        if now.strftime("%A") == "Monday":day_char = MO
        if now.strftime("%A") == "Tuesday":day_char = TU
        if now.strftime("%A") == "Wednesday":day_char = WE
        if now.strftime("%A") == "Thursday":day_char = TH
        if now.strftime("%A") == "Friday":day_char = FR
        if now.strftime("%A") == "Saturday":day_char = SA

        start_date_Y = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_begin.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y");start_date_m = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_begin.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%m");start_date_d = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_begin.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d")
        end_date_Y = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y");end_date_m = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%m");end_date_d = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_id.date_end.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d")
        start_date = datetime(int(start_date_Y),int(start_date_m),int(start_date_d))
        end_date = datetime(int(end_date_Y),int(end_date_m),int(end_date_d))
        end_date_oneplus = end_date+timedelta(days=1)
        

        if self.r_repeat_enddate:
            end_date_Y = datetime.strftime(pytz.utc.localize(datetime.strptime(self.r_repeat_enddate.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%Y");end_date_m = datetime.strftime(pytz.utc.localize(datetime.strptime(self.r_repeat_enddate.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%m");end_date_d = datetime.strftime(pytz.utc.localize(datetime.strptime(self.r_repeat_enddate.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d")
            end_date_r = datetime(int(end_date_Y),int(end_date_m),int(end_date_d))

        if self.r_recurrsion_type == 'monthly':
            if self.r_repeat_end == 'enddate':
                dates = list(rrule(freq=MONTHLY,bysetpos=WEEKLY_INT+1,byweekday=day_char,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                for i in dates:
                    self.eventRecurrsion(i)
            if self.r_repeat_end == 'count':
                # FREQ=MONTHLY;BYSETPOS=1;BYDAY=SU;INTERVAL=1;COUNT=2
                dates = list(rrule(freq=MONTHLY,bysetpos=WEEKLY_INT+1,byweekday=day_char,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                for i in dates:
                    self.eventRecurrsion(i)

        if self.r_recurrsion_type == 'daily':
            if self.r_repeat_end == 'enddate':
                # FREQ=DAILY;INTERVAL=1;UNTIL=20201116T183000Z
                dates = list(rrule(freq=DAILY,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                for i in dates:
                    self.eventRecurrsion(i)
            if self.r_repeat_end == 'count':
                # FREQ=DAILY;INTERVAL=1;COUNT=2
                dates = list(rrule(freq=DAILY,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                for i in dates:
                    self.eventRecurrsion(i)

        if self.r_recurrsion_type == 'week':
            if self.r_repeat_end == 'enddate':
                # FREQ=WEEKLY;BYDAY=MO;INTERVAL=1;UNTIL=20201116T183000Z
                dates = list(rrule(freq=WEEKLY,byweekday=day_char,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                for i in dates:
                    self.eventRecurrsion(i)
            if self.r_repeat_end == 'count':
                # FREQ=WEEKLY;BYDAY=MO;INTERVAL=1;COUNT=2
                dates = list(rrule(freq=WEEKLY,byweekday=day_char,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                for i in dates:
                    self.eventRecurrsion(i)

        if self.r_recurrsion_type == 'annually':
            DAY_D = int(TODAY.strftime("%d"))
            if self.r_repeat_end == 'enddate':
                # FREQ=YEARLY;BYMONTH=11;BYMONTHDAY=16;UNTIL=20201116T183000Z
                dates = list(rrule(freq=YEARLY,bymonth=MONTH_r,bymonthday=DAY_D,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                for i in dates:
                    self.eventRecurrsion(i)
            if self.r_repeat_end == 'count':
                # FREQ=YEARLY;BYMONTH=11;BYMONTHDAY=16;COUNT=2
                dates = list(rrule(freq=YEARLY,bymonth=MONTH_r,bymonthday=DAY_D,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                for i in dates:
                    self.eventRecurrsion(i)

        if self.r_recurrsion_type == 'custom':
            if self.r_repeat_type == 'day':
                if self.r_repeat_end == 'enddate':
                    # FREQ=DAILY;INTERVAL=1;UNTIL=20201116T183000Z
                    dates = list(rrule(freq=DAILY,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                    for i in dates:
                        self.eventRecurrsion(i)
                if self.r_repeat_end == 'count':
                    # FREQ=DAILY;INTERVAL=1;COUNT=2
                    dates = list(rrule(freq=DAILY,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                    for i in dates:
                        self.eventRecurrsion(i)

            if self.r_repeat_type == 'week':
                if self.MO == True:week_days.append(MO)
                if self.TU == True:week_days.append(TU)
                if self.WE == True:week_days.append(WE)
                if self.TH == True:week_days.append(TH)
                if self.FR == True:week_days.append(FR)
                if self.SA == True:week_days.append(SA)
                if self.SU == True:week_days.append(SU)
                if len(week_days) == 0:
                    raise UserError(_("No Days Selected"))
                else:
                    if self.r_repeat_end == 'enddate':
                        # FREQ=WEEKLY;BYDAY=MO;INTERVAL=1;UNTIL=20201116T183000Z
                        dates = list(rrule(freq=WEEKLY,byweekday=week_days,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                        for i in dates:
                            self.eventRecurrsion(i)
                    if self.r_repeat_end == 'count':
                        # FREQ=WEEKLY;BYDAY=MO;INTERVAL=1;COUNT=2
                        dates = list(rrule(freq=WEEKLY,byweekday=week_days,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                        for i in dates:
                            self.eventRecurrsion(i)

            if self.r_repeat_type == 'month':
                DAY_D = int(TODAY.strftime("%d"))
                if self.r_repeat_type_month == 'monthly_word':
                    if self.r_repeat_end == 'enddate':
                        dates = list(rrule(freq=MONTHLY,bysetpos=WEEKLY_INT+1,byweekday=day_char,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                        for i in dates:
                            self.eventRecurrsion(i)
                    if self.r_repeat_end == 'count':
                        # FREQ=MONTHLY;BYSETPOS=1;BYDAY=SU;INTERVAL=1;COUNT=2
                        dates = list(rrule(freq=MONTHLY,bysetpos=WEEKLY_INT+1,byweekday=day_char,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                        for i in dates:
                            self.eventRecurrsion(i)
                if self.r_repeat_type_month == 'monthly_date':
                    if self.r_repeat_end == 'enddate':
                        # FREQ=MONTHLY;BYMONTHDAY=1;INTERVAL=1;UNTIL=20201116T183000Z
                        dates = list(rrule(freq=MONTHLY,bymonthday=DAY_D,interval=self.r_repeat_count,dtstart=end_date_oneplus, until=end_date_r))
                        for i in dates:
                            self.eventRecurrsion(i)
                    if self.r_repeat_end == 'count':
                        # FREQ=MONTHLY;BYSETPOS=1;BYDAY=SU;INTERVAL=1;COUNT=2
                        dates = list(rrule(freq=MONTHLY,bymonthday=DAY_D,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                        for i in dates:
                            self.eventRecurrsion(i)

            if self.r_repeat_type == 'year':
                DAY_D = int(TODAY.strftime("%d"))
                if self.r_repeat_end == 'enddate':
                    # FREQ=YEARLY;BYMONTH=11;BYMONTHDAY=16;UNTIL=20201116T183000Z
                    dates = list(rrule(freq=YEARLY,bymonth=MONTH_r,bymonthday=DAY_D,interval=self.r_repeat_count,dtstart=end_date_oneplus,until=end_date_r))
                    for i in dates:
                        self.eventRecurrsion(i)
                if self.r_repeat_end == 'count':
                    # FREQ=YEARLY;BYMONTH=11;BYMONTHDAY=16;COUNT=2
                    dates = list(rrule(freq=YEARLY,bymonth=MONTH_r,bymonthday=DAY_D,interval=self.r_repeat_count,dtstart=end_date_oneplus,count=self.r_repeat_endcount))
                    for i in dates:
                        self.eventRecurrsion(i)