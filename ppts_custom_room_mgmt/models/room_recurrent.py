from odoo import api, fields, models, _
from dateutil import rrule
import re
from odoo.exceptions import UserError
import babel.dates

import pytz
import babel.dates

from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import time


from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat


class RoomRecurBooking(models.Model):
    _inherit = 'room.booking'

    def recurrent(self):
        print('hi this is test')
        if self.rrule_type == 'weekly':self.recurrent_week()
        if self.rrule_type == 'monthly':self.recurrent_month()
        if self.rrule_type == 'daily':self.recurrent_day()
        if self.rrule_type == 'yearly':self.recurrent_year()

    def recurrent_year(self):
        lastDayTT = lastDay = self.event_end_dt if self.end_type == 'count' else self.final_date
        user_tz = self.env.user.tz or pytz.utc;local = pytz.timezone(user_tz)
        date = self.event_end_dt.strftime('%Y-%m-%d');name = str(self.name + ' (' +date+ ')')
        if self.allday == False:
            start_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_start_dt.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            end_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(lastDayTT.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            start_time = datetime.strptime(start_datetime,'%d-%m-%Y %H:%M:%S');end_time = datetime.strptime(end_datetime,'%d-%m-%Y %H:%M:%S')
            start_time = start_time.strftime('%H:%M');end_time = end_time.strftime('%H:%M');start_time = start_time.replace(":",".");end_time = end_time.replace(":",".")
        else:
            start_time = end_time = 00.00
        use_date = lastDayTT+relativedelta(years=+1)
        name = str(self.name + ' (' +use_date.strftime('%Y-%m-%d')+ ')')
        query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, " \
                "privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES" \
                " ("+"'"+str(name)+"'"+", False,"+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+\
                str(use_date)+"'"+","+"'"+str(use_date)+"'"+", 'room', 'public', 'busy', True,"+str(self.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
        self.env.cr.execute(query)
        self.create({'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),'event_id':self.id,'therapist_id':self.therapist_id.id,'room_id':self.room_id.id,'events_type':self.events_type.id,'event_start_dt':use_date,'event_end_dt':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})

    def recurrent_day(self):
        lastDayTT = lastDay = self.event_end_dt if self.end_type == 'count' else self.final_date
        user_tz = self.env.user.tz or pytz.utc;local = pytz.timezone(user_tz)
        date = self.event_end_dt.strftime('%Y-%m-%d');name = str(self.name + ' (' +date+ ')')
        if self.allday == False:
            start_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(self.event_start_dt
                                                                                   .strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            end_datetime = datetime.strftime(pytz.utc.localize(datetime.strptime(lastDayTT.strftime('%Y-%m-%d %H:%M:%S'),DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local),"%d-%m-%Y %H:%M:%S")
            start_time = datetime.strptime(start_datetime,'%d-%m-%Y %H:%M:%S');end_time = datetime.strptime(end_datetime,'%d-%m-%Y %H:%M:%S')
            start_time = start_time.strftime('%H:%M');end_time = end_time.strftime('%H:%M');start_time = start_time.replace(":",".");end_time = end_time.replace(":",".")
        else:
            start_time = end_time = 00.00
        if self.end_type == 'count':
            use_date = self.event_end_dt
            for i in range(self.count):
                use_date = use_date+relativedelta(days=+1)
                name = str(self.name + ' (' +use_date.strftime('%Y-%m-%d')+ ')')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES ("+"'"+str(name)+"'"+", False,"+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+","+"'"+str(use_date)+"'"+", 'room', 'public', 'busy', True,"+str(self.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
                self.env.cr.execute(query)
                self.create({'name':self.name +' '+ str(use_date.strftime('%Y-%m-%d')),'event_id':self.id,'therapist_id':self.therapist_id.id,'room_id':self.room_id.id,'events_type':self.events_type.id,'event_start_dt':use_date,'event_end_dt':use_date,'address_id':self.address_id.id,'company_id':self.company_id.id})
        else:
            start_date = self.event_end_dt.strftime("%Y-%m-%d")
            end_date = self.final_date
            start_date = datetime.strptime(start_date,"%Y-%m-%d").date()
            def create_events(date):
                name = str(self.name + ' (' +date.strftime('%Y-%m-%d')+ ')')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES ("+"'"+str(name)+"'"+", False,"+"'"+str(date)+"'"+","+"'"+str(date)+"'"+","+"'"+str(date)+"'"+","+"'"+str(date)+"'"+", 'room', 'public', 'busy', True,"+str(self.id)+","+str(self.room_id.id)+","+start_time+","+end_time+");"
                self.env.cr.execute(query)
                self.create({'name':self.name +' '+ str(date.strftime('%Y-%m-%d')),'event_id':self.id,'therapist_id':self.therapist_id.id,'room_id':self.room_id.id,'events_type':self.events_type.id,'event_start_dt':date,'event_end_dt':date,'address_id':self.address_id.id,'company_id':self.company_id.id})
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
        use_date = self.event_end_dt + relativedelta(months=+1)
        lastDayTT = lastDay = self.event_end_dt if self.end_type == 'count' else self.final_date
        user_tz = self.env.user.tz or pytz.utc;
        local = pytz.timezone(user_tz)
        date = use_date.strftime('%Y-%m-%d');
        name = str(self.name + ' (' + date + ')')
        year = int(use_date.strftime('%Y'));
        month = int(use_date.strftime('%m'))
        if self.allday == False:
            start_datetime = datetime.strftime(pytz.utc.localize(
                datetime.strptime(self.event_start_dt
                                  .strftime('%Y-%m-%d %H:%M:%S'),
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
            if self.event_start_dt.strftime('%d') == use_date.strftime('%d'):
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES (" + "'" + str(
                    name) + "'" + ", False," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + "," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + ", 'room', 'public', 'busy', True," + str(self.id) + "," + str(
                    self.room_id.id) + "," + start_time + "," + end_time + ");"
                self.env.cr.execute(query)
                self.create({'name': self.name + ' ' + str(use_date.strftime('%Y-%m-%d')), 'event_id': self.id,
                             'therapist_id': self.therapist_id.id, 'room_id': self.room_id.id,
                             'events_type': self.events_type.id, 'event_start_dt': use_date, 'event_end_dt': use_date,
                             'address_id': self.address_id.id, 'company_id': self.company_id.id})
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
            print(ldates)
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
                date) + "'" + "," + "'" + str(date) + "'" + ", 'room', 'public', 'busy', True," + str(
                self.id) + "," + str(self.event_end_dt.id) + "," + start_time + "," + end_time + ");"
            self.env.cr.execute(query)
            self.create({'event_id': self.event_id,
                         'therapist_id': self.therapist_id.id, 'room_id': self.room_id.id,
                         'room_categ_id': self.room_categ_id.id, 'event_start_dt': use_date, 'event_end_dt': use_date,
                         'event_location_id': self.event_location_id.id, 'room_incharge_id': self.room_incharge_id.id})

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
        firstDay = datetime.strptime(self.event_start_dt.strftime('%d-%B-%Y'), '%d-%B-%Y') + timedelta(days=1)
        lastDay = datetime.strptime(self.event_end_dt.strftime('%d-%B-%Y'), '%d-%B-%Y')
        start_datetime = datetime.strftime(pytz.utc.localize(
            datetime.strptime(self.event_start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                              DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d-%m-%Y %H:%M:%S")
        end_datetime = datetime.strftime(pytz.utc.localize(
            datetime.strptime(self.event_end_dt.strftime('%Y-%m-%d %H:%M:%S'),
                              DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), "%d-%m-%Y %H:%M:%S")
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
                [('booking_type', '=', 'room'), ('room_id', '=', self.room_id.id), ('start_duration', '>=', start_time),
                 ('end_duration', '<=', end_time)])
            if not calendar_id:
                name = str(self.room_id.room_type + ' room Alloted for ' + self.event_id.name);
                date = i.strftime('%Y-%m-%d')
                query = "INSERT INTO calendar_event(name, allday, start_date, stop_date, start, stop, booking_type, privacy, show_as, active ,name_event ,room_id, start_duration, end_duration) VALUES (" + "'" + str(
                    name) + "'" + ", False," + "'" + str(date) + "'" + "," + "'" + str(date) + "'" + "," + "'" + str(
                    date) + "'" + "," + "'" + str(date) + "'" + ", 'room', 'public', 'busy', True," + str(
                    self.event_id.id) + "," + str(self.room_id.id) + "," + start_time + "," + end_time + ");"
                self.env.cr.execute(query)
            else:
                err.append(i)
        if err:
            err_ls = '\n'.join(map(str, err))
            raise UserError(_('Same Room allotted at the same time, Kindly reschedule the date or time!\n %s' % err_ls))
