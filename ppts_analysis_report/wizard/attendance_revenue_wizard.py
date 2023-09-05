from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

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


class AttendanceWizard(models.TransientModel):
    _name = 'attendance.wizard'
    _description="AttendanceWizard"

    date_from = fields.Date("Date from", default=datetime.today())
    date_to = fields.Date("Date to", default=datetime.today())
    company_id = fields.Many2one('res.company', string="Location")
    product_service = fields.Selection([
        ('consu', 'Consumable'), ('product', 'Product'),
        ('service', 'Service')], string='Products/Services')
    payment_method = fields.Selection([('cash', 'Cash'), ('net', 'Net Banking'),
                                       ('bank', 'Bank')], string="Payment Method")
    visit_serv_categ_id = fields.Many2one('appointment.category', string="Visit Service Category")
    date_range = fields.Selection([
        ('year', 'Year'),
        ('quarter', 'Quarter'), ('month', 'Month'),
        ('day', 'Day')], string='Quick Dates')
    staff = fields.Many2one('res.users', string="Staff Members")
    start_time = fields.Selection(TIME, string='Start Time')
    week_list = fields.Selection(
        [('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'),
         ('SA', 'Saturday'), ('SU', 'Sunday')], string='Weekday')
    view = fields.Selection([
        ('summary', 'Summary'),
        ('category', 'Service Category'), ('client', 'Client'), ('staff', 'Staff Member'), ('date', 'Date'),
        ('visit', 'Visit Type'),('noshow_cancel', 'No-shows and Late cancels')], string='View', default='summary')

    def action_apply(self):
        if self.view == 'summary':
            action = self.env.ref('ppts_analysis_report.attendance_summary_action_view').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff_id', '=', self.staff.id)]
                return action
            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action

        elif self.view == 'client':
            action = self.env.ref('ppts_analysis_report.client_view_action_menu').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff', '=', self.staff.id)]
                return action

            # elif self.payment_method == 'cash':
            #     action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
            #     ('payment_method', 'ilike', self.payment_method)]
            #     return action

            # elif self.payment_method == 'net':
            #     action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
            #     ('payment_method', 'ilike', self.payment_method)]
            #     return action

            # elif self.payment_method == 'bank':
            #     action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
            #     ('payment_method', 'ilike', self.payment_method)]
            #     return action

            # elif self.week_list:
            #     action['domain'] = [('date', '>=', self.date_from),('date', '<=', self.date_to),
            #     ('day', 'ilike', self.week_list)]
            #     return action

            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action
        elif self.view == 'category':
            action = self.env.ref('ppts_analysis_report.att_service_categ_action_menu').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff', '=', self.staff.id)]
                return action

            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action

        elif self.view == 'staff':
            action = self.env.ref('ppts_analysis_report.attendance_staff_action_view').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff_id', '=', self.staff.id)]
                return action
            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action

        elif self.view == 'date':
            action = self.env.ref('ppts_analysis_report.attendance_date_action_view').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff_id', '=', self.staff.id)]
                return action
            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action

        elif self.view == 'visit':
            action = self.env.ref('ppts_analysis_report.attendance_visit_type_action_view').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff_id', '=', self.staff.id)]
                return action
            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action

        elif self.view == 'noshow_cancel':
            action = self.env.ref('ppts_analysis_report.noshow_cancels_action_view').read()[0]
            if self.visit_serv_categ_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_serv_categ_id', '=', self.visit_serv_categ_id.id)]
                return action

            elif self.company_id:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('visit_location', '=', self.company_id.id)]
                return action

            elif self.staff:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                                    ('staff_id', '=', self.staff.id)]
                return action
            else:
                action['domain'] = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]
                return action

    @api.onchange('date_range')
    def date_one(self):
        dt = self.date_to
        if self.date_range == 'year':
            y = relativedelta(years=1)
            tot = dt - y
            self.date_from = tot
        if self.date_range == 'quarter':
            q = relativedelta(months=3)
            tot = dt - q
            self.date_from = tot
        if self.date_range == 'month':
            m = relativedelta(days=30)
            tot = dt - m
            self.date_from = tot
        if self.date_range == 'day':
            self.date_from = dt
