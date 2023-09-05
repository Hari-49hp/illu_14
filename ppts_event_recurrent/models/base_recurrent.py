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
 
TIME_T = [('12:00AM','12:00AM'),('12:05AM','12:05AM'),('12:10AM','12:10AM'),('12:15AM','12:15AM'),('12:20AM','12:20AM'),('12:25AM','12:25AM'),('12:30AM','12:30AM'),('12:35AM','12:35AM'),('12:40AM','12:40AM'),('12:45AM','12:45AM'),('12:50AM','12:50AM'),('12:55AM','12:55AM'),('01:00AM','01:00AM'),('01:05AM','01:05AM'),('01:10AM','01:10AM'),('01:15AM','01:15AM'),('01:20AM','01:20AM'),('01:25AM','01:25AM'),('01:30AM','01:30AM'),('01:35AM','01:35AM'),('01:40AM','01:40AM'),('01:45AM','01:45AM'),('01:50AM','01:50AM'),('01:55AM','01:55AM'),('02:00AM','02:00AM'),('02:05AM','02:05AM'),('02:10AM','02:10AM'),('02:15AM','02:15AM'),('02:20AM','02:20AM'),('02:25AM','02:25AM'),('02:30AM','02:30AM'),('02:35AM','02:35AM'),('02:40AM','02:40AM'),('02:45AM','02:45AM'),('02:50AM','02:50AM'),('02:55AM','02:55AM'),('03:00AM','03:00AM'),('03:05AM','03:05AM'),('03:10AM','03:10AM'),('03:15AM','03:15AM'),('03:20AM','03:20AM'),('03:25AM','03:25AM'),('03:30AM','03:30AM'),('03:35AM','03:35AM'),('03:40AM','03:40AM'),('03:45AM','03:45AM'),('03:50AM','03:50AM'),('03:55AM','03:55AM'),('04:00AM','04:00AM'),('04:05AM','04:05AM'),('04:10AM','04:10AM'),('04:15AM','04:15AM'),('04:20AM','04:20AM'),('04:25AM','04:25AM'),('04:30AM','04:30AM'),('04:35AM','04:35AM'),('04:40AM','04:40AM'),('04:45AM','04:45AM'),('04:50AM','04:50AM'),('04:55AM','04:55AM'),('05:00AM','05:00AM'),('05:05AM','05:05AM'),('05:10AM','05:10AM'),('05:15AM','05:15AM'),('05:20AM','05:20AM'),('05:25AM','05:25AM'),('05:30AM','05:30AM'),('05:35AM','05:35AM'),('05:40AM','05:40AM'),('05:45AM','05:45AM'),('05:50AM','05:50AM'),('05:55AM','05:55AM'),('06:00AM','06:00AM'),('06:05AM','06:05AM'),('06:10AM','06:10AM'),('06:15AM','06:15AM'),('06:20AM','06:20AM'),('06:25AM','06:25AM'),('06:30AM','06:30AM'),('06:35AM','06:35AM'),('06:40AM','06:40AM'),('06:45AM','06:45AM'),('06:50AM','06:50AM'),('06:55AM','06:55AM'),('07:00AM','07:00AM'),('07:05AM','07:05AM'),('07:10AM','07:10AM'),('07:15AM','07:15AM'),('07:20AM','07:20AM'),('07:25AM','07:25AM'),('07:30AM','07:30AM'),('07:35AM','07:35AM'),('07:40AM','07:40AM'),('07:45AM','07:45AM'),('07:50AM','07:50AM'),('07:55AM','07:55AM'),('08:00AM','08:00AM'),('08:05AM','08:05AM'),('08:10AM','08:10AM'),('08:15AM','08:15AM'),('08:20AM','08:20AM'),('08:25AM','08:25AM'),('08:30AM','08:30AM'),('08:35AM','08:35AM'),('08:40AM','08:40AM'),('08:45AM','08:45AM'),('08:50AM','08:50AM'),('08:55AM','08:55AM'),('09:00AM','09:00AM'),('09:05AM','09:05AM'),('09:10AM','09:10AM'),('09:15AM','09:15AM'),('09:20AM','09:20AM'),('09:25AM','09:25AM'),('09:30AM','09:30AM'),('09:35AM','09:35AM'),('09:40AM','09:40AM'),('09:45AM','09:45AM'),('09:50AM','09:50AM'),('09:55AM','09:55AM'),('10:00AM','10:00AM'),('10:05AM','10:05AM'),('10:10AM','10:10AM'),('10:15AM','10:15AM'),('10:20AM','10:20AM'),('10:25AM','10:25AM'),('10:30AM','10:30AM'),('10:35AM','10:35AM'),('10:40AM','10:40AM'),('10:45AM','10:45AM'),('10:50AM','10:50AM'),('10:55AM','10:55AM'),('11:00AM','11:00AM'),('11:05AM','11:05AM'),('11:10AM','11:10AM'),('11:15AM','11:15AM'),('11:20AM','11:20AM'),('11:25AM','11:25AM'),('11:30AM','11:30AM'),('11:35AM','11:35AM'),('11:40AM','11:40AM'),('11:45AM','11:45AM'),('11:50AM','11:50AM'),('11:55AM','11:55AM'),('12:00PM','12:00PM'),('12:05PM','12:05PM'),('12:10PM','12:10PM'),('12:15PM','12:15PM'),('12:20PM','12:20PM'),('12:25PM','12:25PM'),('12:30PM','12:30PM'),('12:35PM','12:35PM'),('12:40PM','12:40PM'),('12:45PM','12:45PM'),('12:50PM','12:50PM'),('12:55PM','12:55PM'),('01:00PM','01:00PM'),('01:05PM','01:05PM'),('01:10PM','01:10PM'),('01:15PM','01:15PM'),('01:20PM','01:20PM'),('01:25PM','01:25PM'),('01:30PM','01:30PM'),('01:35PM','01:35PM'),('01:40PM','01:40PM'),('01:45PM','01:45PM'),('01:50PM','01:50PM'),('01:55PM','01:55PM'),('02:00PM','02:00PM'),('02:05PM','02:05PM'),('02:10PM','02:10PM'),('02:15PM','02:15PM'),('02:20PM','02:20PM'),('02:25PM','02:25PM'),('02:30PM','02:30PM'),('02:35PM','02:35PM'),('02:40PM','02:40PM'),('02:45PM','02:45PM'),('02:50PM','02:50PM'),('02:55PM','02:55PM'),('03:00PM','03:00PM'),('03:05PM','03:05PM'),('03:10PM','03:10PM'),('03:15PM','03:15PM'),('03:20PM','03:20PM'),('03:25PM','03:25PM'),('03:30PM','03:30PM'),('03:35PM','03:35PM'),('03:40PM','03:40PM'),('03:45PM','03:45PM'),('03:50PM','03:50PM'),('03:55PM','03:55PM'),('04:00PM','04:00PM'),('04:05PM','04:05PM'),('04:10PM','04:10PM'),('04:15PM','04:15PM'),('04:20PM','04:20PM'),('04:25PM','04:25PM'),('04:30PM','04:30PM'),('04:35PM','04:35PM'),('04:40PM','04:40PM'),('04:45PM','04:45PM'),('04:50PM','04:50PM'),('04:55PM','04:55PM'),('05:00PM','05:00PM'),('05:05PM','05:05PM'),('05:10PM','05:10PM'),('05:15PM','05:15PM'),('05:20PM','05:20PM'),('05:25PM','05:25PM'),('05:30PM','05:30PM'),('05:35PM','05:35PM'),('05:40PM','05:40PM'),('05:45PM','05:45PM'),('05:50PM','05:50PM'),('05:55PM','05:55PM'),('06:00PM','06:00PM'),('06:05PM','06:05PM'),('06:10PM','06:10PM'),('06:15PM','06:15PM'),('06:20PM','06:20PM'),('06:25PM','06:25PM'),('06:30PM','06:30PM'),('06:35PM','06:35PM'),('06:40PM','06:40PM'),('06:45PM','06:45PM'),('06:50PM','06:50PM'),('06:55PM','06:55PM'),('07:00PM','07:00PM'),('07:05PM','07:05PM'),('07:10PM','07:10PM'),('07:15PM','07:15PM'),('07:20PM','07:20PM'),('07:25PM','07:25PM'),('07:30PM','07:30PM'),('07:35PM','07:35PM'),('07:40PM','07:40PM'),('07:45PM','07:45PM'),('07:50PM','07:50PM'),('07:55PM','07:55PM'),('08:00PM','08:00PM'),('08:05PM','08:05PM'),('08:10PM','08:10PM'),('08:15PM','08:15PM'),('08:20PM','08:20PM'),('08:25PM','08:25PM'),('08:30PM','08:30PM'),('08:35PM','08:35PM'),('08:40PM','08:40PM'),('08:45PM','08:45PM'),('08:50PM','08:50PM'),('08:55PM','08:55PM'),('09:00PM','09:00PM'),('09:05PM','09:05PM'),('09:10PM','09:10PM'),('09:15PM','09:15PM'),('09:20PM','09:20PM'),('09:25PM','09:25PM'),('09:30PM','09:30PM'),('09:35PM','09:35PM'),('09:40PM','09:40PM'),('09:45PM','09:45PM'),('09:50PM','09:50PM'),('09:55PM','09:55PM'),('10:00PM','10:00PM'),('10:05PM','10:05PM'),('10:10PM','10:10PM'),('10:15PM','10:15PM'),('10:20PM','10:20PM'),('10:25PM','10:25PM'),('10:30PM','10:30PM'),('10:35PM','10:35PM'),('10:40PM','10:40PM'),('10:45PM','10:45PM'),('10:50PM','10:50PM'),('10:55PM','10:55PM'),('11:00PM','11:00PM'),('11:05PM','11:05PM'),('11:10PM','11:10PM'),('11:15PM','11:15PM'),('11:20PM','11:20PM'),('11:25PM','11:25PM'),('11:30PM','11:30PM'),('11:35PM','11:35PM'),('11:40PM','11:40PM'),('11:45PM','11:45PM'),('11:50PM','11:50PM'),('11:55PM','11:55PM')]
dTIME_T = [('12:00AM','12:00AM'),('12:30AM','12:30AM'),('01:00AM','01:00AM'),('01:30AM','01:30AM'),('02:00AM','02:00AM'),('02:30AM','02:30AM'),('03:00AM','03:00AM'),('03:30AM','03:30AM'),('04:00AM','04:00AM'),('04:30AM','04:30AM'),('05:00AM','05:00AM'),('05:30AM','05:30AM'),('06:00AM','06:00AM'),('06:30AM','06:30AM'),('07:00AM','07:00AM'),('07:30AM','07:30AM'),('08:00AM','08:00AM'),('08:30AM','08:30AM'),('09:00AM','09:00AM'),('09:30AM','09:30AM'),('10:00AM','10:00AM'),('10:30AM','10:30AM'),
          ('11:00AM','11:00AM'),('11:30AM','11:30AM'),('12:00PM','12:00PM'),('12:30PM','12:30PM'),('01:00PM','01:00PM'),('01:30PM','01:30PM'),('02:00PM','02:00PM'),('02:30PM','02:30PM'),('03:00PM','03:00PM'),('03:30PM','03:30PM'),('04:00PM','04:00PM'),('04:30PM','04:30PM'),('05:00PM','05:00PM'),
          ('05:30PM','05:30PM'),('06:00PM','06:00PM'),('06:30PM','06:30PM'),('07:00PM','07:00PM'),('07:30PM','07:30PM'),('08:00PM','08:00PM'),('08:30PM','08:30PM'),('09:00PM','09:00PM'),('09:30PM','09:30PM'),('10:00PM','10:00PM'),('10:30PM','10:30PM'),('11:00PM','11:00PM'),('11:30PM','11:30PM')]


class BaseRecurrent(models.Model):
    _name = 'base.recurrent'
    _description = 'Recurrent'
    _rec_name = 'event_id'

    base_multi_select = fields.Selection([('single','Single Date'),('multi','Multi Date')],default='single')
    state = fields.Selection([('draft','Draft'),('created','Created')],default='draft')
    start = fields.Date('Date')
    start_time = fields.Selection(TIME_T,'Start Time')
    end_time = fields.Selection(TIME_T,'End Time')
    multi_select_date = fields.Char('Multi Select Date')
    event_id = fields.Many2one('event.event',string='Event')
    event_type = fields.Many2one('event.type',string='Event Type',related="event_id.event_type_id")
    recurrent_ids = fields.One2many('base.recurrent.line','recurrent_id', string='Date')
    base_recurrent_id = fields.Many2one('base.recurrent', string='Base Recurrent')
    stop = fields.Datetime('End Date')
    duration = fields.Float('Duration')
    allday = fields.Boolean('All day')

    @api.onchange('start_time','end_time')
    def _onchange_event_time(self):
        for rec in self:
            start_time = datetime.strptime(str(rec.start_time), "%H:%M%p")
            start_time = float(start_time.strftime("%H.%M"))
            end_time = datetime.strptime(str(rec.end_time), "%H:%M%p")
            end_time = float(end_time.strftime("%H.%M"))
            if end_time<start_time:
                self.duration=abs(end_time-start_time)
            else:
                self.duration=abs(end_time-start_time)

    def base_recurrent_event_rec(self):
        if self.recurrent_ids:
            for i in self.recurrent_ids:
                if i.recurrent_id_active != True:    
                    base_ids = self.create({
                        'start':i.selected_date,
                        'start_time':i.start_time,
                        'end_time':i.end_time,
                        'event_id':self.event_id.id,
                        })
                    i.recurrent_id_active = True
                    i.base_recurrent_line_id = base_ids.id
                else:
                    if i.base_recurrent_line_id:
                        i.base_recurrent_line_id.write({
                            'start':i.selected_date,
                            'start_time':i.start_time,
                            'end_time':i.end_time,
                            })
        self.event_id.base_recurrent_event()

        return {'type': 'ir.actions.act_window_close'}

    def multi_process(self):
        dates = str(self.multi_select_date).split(",")
        for i in dates:
            aa_date = datetime.strptime(str(i), "%m/%d/%Y")
            a_date = date(int(aa_date.strftime("%Y")), int(aa_date.strftime("%m")), int(aa_date.strftime("%d")))
            recurrent_line_ids = self.env['base.recurrent.line'].search([('recurrent_id','=',self.id),('selected_date','=',a_date)])
            if not recurrent_line_ids and self.event_id:
                self.env['base.recurrent.line'].create({
                    'selected_date':a_date,
                    'recurrent_id':self.id,
                    'start_time':self.event_id.date_begin.strftime('%I:%M%p'),
                    'end_time':self.event_id.date_end.strftime('%I:%M%p')
                    })

class BaseRecurrentLine(models.Model):
    _name = 'base.recurrent.line'
    _description = 'Recurrent Line'
    _rec_name = 'selected_date'

    selected_date = fields.Date('Date',required=True)
    start_time = fields.Selection(TIME_T,'Start Time',required=True)
    end_time = fields.Selection(TIME_T,'End Time',required=True)
    duration = fields.Float(string='Duration')

    recurrent_id = fields.Many2one('base.recurrent','Recurrent')
    recurrent_id_active = fields.Boolean('Recurrent')
    base_recurrent_line_id = fields.Many2one('base.recurrent', string='Base Recurrent')

    @api.onchange('start_time','end_time')
    def _onchange_event_time(self):
        for rec in self:
            start_time = datetime.strptime(str(rec.start_time), "%H:%M%p")
            start_time = float(start_time.strftime("%H.%M"))

            end_time = datetime.strptime(str(rec.end_time), "%H:%M%p")
            end_time = float(end_time.strftime("%H.%M"))
            if end_time<start_time:
                self.duration=abs(end_time-start_time)
            else:
                self.duration=abs(end_time-start_time)