from datetime import date, datetime, timedelta, time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

import datetime
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import pytz


class MultiDateWizard(models.Model):
    _name = "multi.date.wizard"
    _description ="MultiDateWizard"

    hour_time = [
                ('01', "01"),
                ('02', "02"),
                ('03', "03"),
                ('04', "04"),
                ('05', "05"),
                ('06', "06"),
                ('07', "07"),
                ('08', "08"),
                ('09', "09"),
                ('10', "10"),
                ('11', "11"),
                ('12', "12"),
                 ('13', "13"),
                 ('14', "14"),
                 ('15', "15"),
                 ('16', "16"),
                 ('17', "17"),
                 ('18', "18"),
                 ('19', "19"),
                 ('20', "20"),
                 ('21', "21"),
                 ('22', "22"),
                 ('23', "23")];

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
                 ('55', "55")]


    event_wiz_id = fields.Many2one('event.event', string="Event")
    company_id = fields.Many2one('res.company', string='Company',required=False)
    facilitator_evnt_ids=fields.Many2many('hr.employee',string='Facilitator ',help='List of Facilitators Name')
    available_dates_list = fields.Char('Date List')
    multi_date_select = fields.Char('Select Date')
    duration = fields.Float(string='Total Duration', compute='_compute_duration_tot', store=True, copy=False)
    w_multi_date_ids = fields.One2many('wiz.multi.date.line','wiz_id',string='Select Date')
    
    date_begin = fields.Date(string='Start Date')
    hour_time_begin = fields.Selection(hour_time, string='Hours', copy=False)
    min_time_begin = fields.Selection(min_time, string='Minutes', copy=False,default='00')

    date_end = fields.Date(string='End Date')
    hour_time_end = fields.Selection(hour_time, string='Hours', copy=False)
    min_time_end = fields.Selection(min_time, string='Minutes', copy=False,default='00')
    multidate_inv = fields.Boolean(string="Multidate Invisible",help="Help to invisible and visible the fields")
    multidate_page_inv = fields.Boolean(strind="Multidate Page Invisible",help="To invisible the pages")

    @api.onchange('facilitator_evnt_ids')
    def action_set_facilitator_domain(self):
        therapist_ids=self.env['hr.employee.category'].search([('name', 'ilike','Facilitator')])
        get_facilitator = self.env['hr.employee'].search([('employee_type','in',therapist_ids.ids)])
        return {'domain': {'facilitator_evnt_ids': [('id','in',get_facilitator.ids)]}}



    @api.onchange('facilitator_evnt_ids','date_begin','date_end')
    def _onchange_facilitator_availability(self):
        if self.facilitator_evnt_ids:
            lstt = []; date_list = ''
            avail_id = self.env['availability.availability'].search([('facilitator','in',self.facilitator_evnt_ids.ids),\
                    ('date_range','=','ongoing'),('available_date','>', datetime.now().date().strftime("%Y-%m-%d"))])

            for i in avail_id:
                date_id = self.env['date.date'].search([('date','=',i.available_date.strftime("%Y-%m-%d"))],limit=1)
                if date_id:   
                    lstt.append(date_id.id)
                    date_list += date_id.date.strftime("%m/%d/%Y") +','
            date_list = date_list[:-1]
            self.available_dates_list = date_list

    @api.onchange('facilitator_evnt_ids','room_id')
    def _onchange_multidate_invisible(self):
        if self.facilitator_evnt_ids and self.room_id:
            self.multidate_inv = True
        else:
            self.multidate_inv = False






    #to load default values on wizard

    @api.onchange('date_begin','hour_time_begin','min_time_begin','date_end','hour_time_end','min_time_end')
    def _onchange_set_dates(self):
        if self.date_begin and self.hour_time_begin and\
            self.min_time_begin and self.date_end and self.hour_time_end and self.min_time_end:
            self.set_dates_in()

    def set_dates_in(self):
        sdate = self.date_begin; edate = self.date_end
        delta = edate - sdate
        line_ids = []; app_line = []
        for l in self.w_multi_date_ids:
            line_ids.append(l._origin.id)

        def create_line():
            for i in range(delta.days + 1):
                day = sdate + timedelta(days=i)
                setl = day.strftime("%m/%d/%Y")
                app_line.append([0, 0, {
                        "date_begin": datetime.strptime(setl, "%m/%d/%Y"),
                        "date_end": datetime.strptime(setl, "%m/%d/%Y"),
                        "hour_time_begin": self.hour_time_begin,
                        "min_time_begin": self.min_time_begin,
                        "hour_time_end":self.hour_time_end,
                        "min_time_end":self.min_time_end,
                        "wiz_id": self.id,
                    }])
            
            self.w_multi_date_ids = app_line
        if self.w_multi_date_ids:
            self.w_multi_date_ids = False
            create_line()
        else:
            create_line()
        for each in self.w_multi_date_ids:
            each._onchangeddd_min_time_end()

    @api.onchange('event_wiz_id')
    def _onchange_lineitems_add(self):
        wiz_line_obj = self.env['wiz.multi.date.line']
        for lst_ids in self.event_wiz_id.multi_date_line_ids:
            wiz_line_obj.create({
                'wiz_id': self.id,
                'date_begin':lst_ids.date_begin,
                'hour_time_begin':lst_ids.hour_time_begin,
                'min_time_begin':lst_ids.min_time_begin,
                'm_date_begin':lst_ids.m_date_begin,
                'date_end':lst_ids.date_end,
                'hour_time_end':lst_ids.hour_time_end,
                'min_time_end':lst_ids.min_time_end,
                'm_date_end':lst_ids.m_date_end,
                'duration': lst_ids.duration})

    @api.depends('w_multi_date_ids')
    def _compute_duration_tot(self):
        for each in self:
            each.duration = 0
            def diff(t_a, t_b):
                        t_diff = relativedelta(t_b, t_a)  # later/end time comes first!
                        return str(t_diff.hours)+':'+str(t_diff.minutes)+':'+str(t_diff.seconds)

            h = []
            for i in each.w_multi_date_ids:
                a = datetime(2022, 1, 18, int(i.hour_time_begin), int(i.min_time_begin), 00)
                b = datetime(2022, 1, 18, int(i.hour_time_end), int(i.min_time_end), 00)                    
                h.append(diff(a,b))
            def to_td(h):
                ho, mi, se = h.split(':')
                return timedelta(hours=int(ho), minutes=int(mi), seconds=int(se))
            totalSecs = 0
            hr = 0
            min =0
            for tm in h:
                timeParts = [int(s) for s in tm.split(':')]
                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
            totalSecs, sec = divmod(totalSecs, 60)
            hr, min = divmod(totalSecs, 60)
            each.duration= (float(str( "%d:%02d:%02d" % (hr, min, sec)).replace(':','.')[:-3]))

    # made some changes in multidate in event 10-09-22
    def submit_multidate_wiz(self):
        if not self.duration:
            raise UserError('Please Select Correct Date & Time for Event!')
        else:
            if self.env.context.get('active_id'):
                cur_event_id = self.env['event.event'].browse(self.env.context.get('active_id'))
                if not cur_event_id.multi_date_line_ids:
                    tot_duration =0.0
                    cur_event_id.facilitator_evnt_ids = self.facilitator_evnt_ids.ids 
                    cur_event_id.room_id = self.room_id.id
                    for m_date in cur_event_id.multi_date_line_ids:
                        m_date.unlink()
                    dates_list = []
                    for lst_ids in self.w_multi_date_ids:
                        dates_list.append(lst_ids.m_date_begin)
                        dates_list.append(lst_ids.m_date_end)
                        vals={
                            'date_begin':lst_ids.date_begin,
                            'hour_time_begin':lst_ids.hour_time_begin,
                            'min_time_begin':lst_ids.min_time_begin,
                            'm_date_begin':lst_ids.m_date_begin,
                            'date_end':lst_ids.date_end,
                            'hour_time_end':lst_ids.hour_time_end,
                            'min_time_end':lst_ids.min_time_end,
                            'm_date_end':lst_ids.m_date_end,
                            'duration':lst_ids.duration,
                            'event_id':cur_event_id.id}
                        cur_event_id.multi_date_line_ids.create(vals)
                    min_date = min(dates_list)
                    max_date = max(dates_list)
                    # pass the start and end date value for multidate  11-08-22
                    cur_event_id.write({'date_begin': min_date, 'date_end': max_date,'multiday':True,'duration':self.duration,
                        'event_start':self.date_begin,'event_end':self.date_end,'start_end_date':True})
                    
                    self.event_wiz_id.onchange_facilitator_evnt_ids_set()
                    cur_event_id.therapist_multidate_room_validation()
                    cur_event_id.multidate_room_validation()
                else:
                    tot_duration =0.0
                    cur_event_id.facilitator_evnt_ids = self.facilitator_evnt_ids.ids 
                    cur_event_id.room_id = self.room_id.id
                    for m_date in cur_event_id.multi_date_line_ids:
                        m_date.unlink()
                    dates_list = []
                    for lst_ids in self.w_multi_date_ids:
                        dates_list.append(lst_ids.m_date_begin)
                        dates_list.append(lst_ids.m_date_end)
                        vals={
                            'date_begin':lst_ids.date_begin,
                            'hour_time_begin':lst_ids.hour_time_begin,
                            'min_time_begin':lst_ids.min_time_begin,
                            'm_date_begin':lst_ids.m_date_begin,
                            'date_end':lst_ids.date_end,
                            'hour_time_end':lst_ids.hour_time_end,
                            'min_time_end':lst_ids.min_time_end,
                            'm_date_end':lst_ids.m_date_end,
                            'duration':lst_ids.duration,
                            'event_id':cur_event_id.id}
                        cur_event_id.multi_date_line_ids.create(vals)
                    min_date = min(dates_list)
                    max_date = max(dates_list)
                    # pass the start and end date value for multidate 11-08-22
                    cur_event_id.write({'date_begin': min_date, 'date_end': max_date,'multiday':True,'duration':self.duration,
                        'event_start':self.date_begin,'event_end':self.date_end})
                    self.event_wiz_id.onchange_facilitator_evnt_ids_set()
                    cur_event_id.therapist_multidate_room_validation()
                    cur_event_id.multidate_room_validation()
                
        return True

class WizMultiDateLine(models.Model):
    _name = 'wiz.multi.date.line'
    _description ="MultiDateWizardLine"

    hour_time = [
                ('01', "01"),
                ('02', "02"),
                ('03', "03"),
                ('04', "04"),
                ('05', "05"),
                ('06', "06"),
                ('07', "07"),
                ('08', "08"),
                ('09', "09"),
                ('10', "10"),
                ('11', "11"),
                ('12', "12"),
                 ('13', "13"),
                 ('14', "14"),
                 ('15', "15"),
                 ('16', "16"),
                 ('17', "17"),
                 ('18', "18"),
                 ('19', "19"),
                 ('20', "20"),
                 ('21', "21"),
                 ('22', "22"),
                 ('23', "23")];
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
                 ('55', "55")]

    wiz_id = fields.Many2one('multi.date.wizard', string="Event")
    date_begin = fields.Date(string='Start Date')
    hour_time_begin = fields.Selection(hour_time, string='Hours', copy=False)
    min_time_begin = fields.Selection(min_time, string='Minutes', copy=False,default='00')
    m_date_begin = fields.Datetime(string='Start Date Time')
    date_end = fields.Date(string='End Date',related="date_begin")
    hour_time_end = fields.Selection(hour_time, string='Hours', copy=False)
    min_time_end = fields.Selection(min_time, string='Minutes', copy=False,default='00')
    m_date_end = fields.Datetime(string='End Date Time')
    duration = fields.Float(string='Duration',compute='_compute_duration',store=True, copy=False)

    @api.onchange('min_time_end', 'hour_time_end', 'hour_time_begin', 'min_time_begin', 'date_begin')
    def _onchangeddd_min_time_end(self):

       if self.date_begin and self.hour_time_begin and self.min_time_begin and self.hour_time_end and self.min_time_end:
        now_year = self.date_begin.year
        now_month = self.date_begin.month
        now_date = self.date_begin.day
        now_hr = int(self.hour_time_begin)
        now_min = int(self.min_time_begin)
        now_sec = 00
        now_hr_e = int(self.hour_time_end)
        now_min_e = int(self.min_time_end)
        local_tz = pytz.timezone(self.wiz_id.event_wiz_id.date_tz)
        date_begin = local_tz.localize(datetime(now_year, now_month, now_date, now_hr, now_min, now_sec)).astimezone(
            pytz.utc).replace(tzinfo=None)
        date_end = local_tz.localize(datetime(now_year, now_month, now_date, now_hr_e, now_min_e, now_sec)).astimezone(
            pytz.utc).replace(tzinfo=None)
        self.m_date_begin = date_begin
        self.m_date_end = date_end

    @api.depends('m_date_end', 'm_date_begin')
    def _compute_duration(self):
        for rec in self:
            if rec.m_date_end and rec.m_date_begin:
                if rec.m_date_end<rec.m_date_begin:
                    raise UserError('Please Select Date & Time for Event!')
                else:
                    duration = (rec.m_date_end-rec.m_date_begin)
                    start_time = datetime.strptime(str(duration), "%H:%M:%S")
                    start_time = start_time.strftime("%H.%M")
                    rec.duration = float(start_time)
