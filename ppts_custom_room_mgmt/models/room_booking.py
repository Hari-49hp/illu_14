from odoo import api, fields, models, _
from dateutil import rrule
import re
from odoo.exceptions import UserError
import babel.dates
from datetime import date, timedelta, datetime
import time

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat


class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Event Room Booking'
    _rec_name = 'event_id'

    event_id = fields.Many2one('event.event',string='Event Name',required=True)
    therapist_id = fields.Many2one('res.partner',string='Therapist',required=True)
    room_categ_id = fields.Many2one('room.maincateg.master',string='Serivce Category',required=True)
    event_start_dt = fields.Datetime(string='Start Date',related='event_id.date_begin', readonly='True')
    event_end_dt = fields.Datetime(string='End Date',related='event_id.date_end', readonly='True')
    room_id = fields.Many2one('roomtype.master',string='Room')
    event_location_id = fields.Many2one('venue.venue',related='event_id.address_id',string='Location',required=True)
    appointment_id = fields.Many2one('calendar.appointment.type',string='Appointment')
    room_incharge_id = fields.Many2one('hr.employee',string='Room Incharge',required=True)
    duration = fields.Float('Duration')
    allday = fields.Boolean('All Day', default=False)
    description = fields.Text('Description')
    #recurent
    rrule = fields.Char('Recurrent Rule', compute='_compute_rrule', inverse='_inverse_rrule', store=True)
    rrule_type = fields.Selection([
        ('daily', 'Days'),
        ('weekly', 'Weeks'),
        ('monthly', 'Months'),
        ('yearly', 'Years')
    ], string='Recurrence',
        help="Let the event automatically repeat at that interval")
    recurrency = fields.Boolean('Recurrent', help="Recurrent Meeting")
    recurrent_id = fields.Integer('Recurrent ID')
    recurrent_id_date = fields.Datetime('Recurrent ID date')
    end_type = fields.Selection([
        ('count', 'Number of repetitions'),
        ('end_date', 'End date')
    ], string='Recurrence Termination', default='end_date')
    interval = fields.Integer(string='Repeat Every', default=1, help="Repeat every (Days/Week/Month/Year)")
    count = fields.Integer(string='Repeat', help="Repeat x times", default=1)
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    month_by = fields.Selection([
        ('date', 'Date of month'),
        ('day', 'Day of month')
    ], string='Option', default='date')
    day = fields.Integer('Date of month', default=1)
    week_list = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday')
    byday = fields.Selection([
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Fourth'),
        ('5', 'Fifth'),
        ('-1', 'Last')
    ], string='By day')
    final_date = fields.Datetime('Repeat Until', related="event_id.date_end", required=True)

    #fumctions
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
        """ get the display_time of the meeting, forcing the timezone. This method is called from email template, to not use sudo(). """
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
            data.update(
                values,
                recurrent_id=real_id,
                recurrent_id_date=data.get('start'),
                rrule_type=False,
                rrule='',
                recurrency=False,
                final_date=False,
                end_type=False
            )
            # do not copy the id
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

    @api.onchange('start_datetime','stop_datetime')
    def _onchange_duration(self):
        if self.start_datetime:
            self.duration  = self._get_duration(self.start_datetime,self.stop_datetime)


    def _get_duration(self, start_datetime, stop_datetime):
        """ Get the duration value between the 2 given dates. """
        if start_datetime and stop_datetime:
            diff = fields.Datetime.from_string(stop_datetime) - fields.Datetime.from_string(start_datetime)
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)
                return round(duration, 2)
            return 0.0

    def event_calendar_create(self):

        start=self.start_datetime
        end=self.stop_datetime
        alldays=self.allday
        name="Room for "+self.event_id.name
        print("date time", name)
        calendar_event = self.env['calendar.event'].create({
            'name': name,
            'start': start,
            'start_datetime': start,
            'stop': end,
            'stop_datetime': end,
            'allday': alldays,
        })

    def recurrent(self):
        if self.rrule_type == 'weekly':self.recurrent_week()

    def recurrent_week(self):
        import pytz
        weekday_en = [];req_dates = [];err = []
        user_tz = self.env.user.tz or pytz.utc;local = pytz.timezone(user_tz)
        if self.mo == True:weekday_en.append('Monday')
        if self.tu == True:weekday_en.append('Tuesday')
        if self.we == True:weekday_en.append('Wednesday')
        if self.th == True:weekday_en.append('Thursday')
        if self.fr == True:weekday_en.append('Friday')
        if self.sa == True:weekday_en.append('Saturday')
        if self.su == True:weekday_en.append('Sunday')
        firstDay = datetime.strptime(self.event_start_dt.strftime('%d-%B-%Y'), '%d-%B-%Y')+timedelta(days=1) 
        lastDay = datetime.strptime(self.event_end_dt.strftime('%d-%B-%Y'), '%d-%B-%Y')
        start_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_start_dt.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_end_dt.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
        start_time = datetime.strptime(start_datetime,'%d-%m-%Y %H:%M:%S');end_time = datetime.strptime(end_datetime,'%d-%m-%Y %H:%M:%S')
        start_time = start_time.strftime('%H:%M');end_time = end_time.strftime('%H:%M');start_time = start_time.replace(":",".");end_time = end_time.replace(":",".")
        for weekDay in weekday_en:
            req_dates.append([firstDay + timedelta(days=x) for x in range((lastDay-firstDay).days + 1) if (firstDay + timedelta(days=x)).weekday() == time.strptime(weekDay, '%A').tm_wday])
        req_dates_all  = [val for sublist in req_dates for val in sublist]
        for i in req_dates_all:
            calendar_id = self.env['calendar.event'].search([('booking_type','=','room'),('room_id','=',self.room_id.id),('start_duration','>=',start_time),('end_duration','<=',end_time)])
            if not calendar_id:
                name = str(self.room_id.room_type+' room Alloted for '+self.event_id.name);date = i.strftime('%Y-%m-%d')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES ("+"'"+str(name)+"'"+", False,"+"'"+str(date)+"'"+","+"'"+str(date)+"'"+","+"'"+str(date)+"'"+","+"'"+str(date)+"'"+", 'room', 'public', 'busy', True,"+str(self.event_id.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
                self.env.cr.execute(query)
            else:
                err.append(i)
        if err:
            err_ls = '\n'.join(map(str, err))
            raise UserError(_('Same Room allotted at the same time, Kindly reschedule the date or time!\n %s' %err_ls))