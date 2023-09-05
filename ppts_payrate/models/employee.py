from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    service_category_ids = fields.Many2many('appointment.category',string='Services Category',compute='_compute_pay_rate_ids',store=True)
    pay_rate_ids = fields.One2many('hr.employee.payrate','employee_id',string='Pay Rate')

    def website_emp_payrate(self):
        lst = []
        for i in self.pay_rate_ids:
            lst.append(i.service_category_type_id.name)
        return set(lst)

    def write(self, vals):
        write_val=super(HrEmployee, self).write(vals)
        s_list_id = []
        for emp_obj in self:
            for rec in emp_obj.pay_rate_ids:
                emp_id=emp_obj.id
                if rec.service_category_type_id and rec.appoinment_type_id:
                    emp_list = self.env['staff.list.line'].search([
                        ('employee_id', '=', emp_id), ('appointment_id', '=', rec.appoinment_type_id.id)])
                    for emp in emp_list:
                        emp.unlink()
                    sub_categories = self.env['calendar.appointment.type'].search([
                        ('service_categ_id', '=', rec.service_category_type_id.id), ('id', '=', rec.appoinment_type_id.id)])
                    # create new line
                    for subs in sub_categories:
                        rc_promo_vals = {
                            'appointment_id': rec.appoinment_type_id.id,
                            'service_categ_id': rec.service_category_type_id.id,
                            'pay_rate_id': rec.id,
                            'employee_id': emp_id,
                            'time_id': rec.duration_id.id,
                            'course_unit_price': rec.unit_price,
                            'pay_type':rec.staff_rate,
                            'unit_price': rec.staff_rate_percentage,
                        }
                        rc_sale_order_id = self.env['staff.list.line'].create(rc_promo_vals)
                else:
                    sub_categories = self.env['calendar.appointment.type'].search([
                        ('service_categ_id', '=', rec.service_category_type_id.id)])
                    emp_list = self.env['staff.list.line'].search([
                        ('employee_id', '=', emp_id), ('service_categ_id', '=', rec.service_category_type_id.id)])
                    for emp in emp_list:
                        emp.unlink()
                    for apt in sub_categories:
                        rc_promo_vals = {
                            'appointment_id': apt.id,
                            'service_categ_id': rec.service_category_type_id.id,
                            'pay_rate_id': rec.id,
                            'employee_id': emp_id,
                            'time_id': rec.duration_id.id,
                            'course_unit_price': rec.unit_price,
                            'pay_type':rec.staff_rate,
                            'unit_price': rec.staff_rate_percentage,
                        }
                        rc_sale_order_id = self.env['staff.list.line'].create(rc_promo_vals)

    @api.depends('pay_rate_ids')
    def _compute_pay_rate_ids(self):
        s_list_id = []
        for rec in self:
            for service in rec.pay_rate_ids:
                # added condition for deletion issue in the service details 19-10-22
                if service.service_category_type_id:
                    s_list_id.append(service.service_category_type_id.id)
        rec.service_category_ids=[(6, 0, s_list_id)]

class HrEmployeePayrate(models.Model):
    _name = 'hr.employee.payrate'
    _description="HrEmployeePayrate"
    _rec_name = 'employee_id'
    _sql_constraints = [('hr_employee_duration_id_uniq', 'unique (employee_id,service_category_type_id,appoinment_type_id,duration_id)',     
                'Service Detail already given')]

    service_category_type_id = fields.Many2one('appointment.category','Service Category')
    appoinment_type_id = fields.Many2one('calendar.appointment.type','Sub Category')

    def _compute_length_apt_fetch(self):
        for apt in self:
            if apt:
                lengthv=self.env['calendar.appointment.type'].search([('id', '=', apt.appoinment_type_id.id)]).appointment_duration
                apt.write({'length':lengthv})
    #compute='_compute_length_apt_fetch',
    length = fields.Float('Length mins',store=True)
    duration_id=fields.Many2one('time.time','Duration')
    staff_rate = fields.Selection([('no_pay','No Pay'),
                                   ('flat_rate','Flat Rate'),
                                   ('percentage_rate','Percentage Rate')],
                                  string='Pay Rate Type',
                                  default='percentage_rate',required=True)
    staff_rate_percentage = fields.Float('Pay Rate')
    unit_price_type = fields.Char(string=' ', compute='_compute_unit_price_type', store='True')
    unit_price = fields.Float('Price')
    employee_id = fields.Many2one('hr.employee',string='Employee')

    @api.onchange('service_category_type_id','appoinment_type_id','duration_id')
    def _onchange_domain_payrate_line(self):
        if self.service_category_type_id and self.appoinment_type_id and self.duration_id:
            for i in self.employee_id.pay_rate_ids._origin:
                if self.service_category_type_id.id == i.service_category_type_id.id and \
                    self.appoinment_type_id.id == i.appoinment_type_id.id and \
                        self.duration_id.id == i.duration_id.id:

                    raise ValidationError(_("Service Detail already given"))

    @api.onchange('service_category_type_id')
    def onchange_service_category_type_id(self):
        self.appoinment_type_id = False
        self.duration_id = False
        self.unit_price = 0.00
        self.staff_rate = 'percentage_rate'
        self.staff_rate_percentage = 0.00

    @api.depends('staff_rate')
    def _compute_unit_price_type(self):
        for rec in self:
            if rec.staff_rate == 'flat_rate':
                cur = self.env.company.currency_id.name
                rec.unit_price_type = cur
            elif rec.staff_rate == 'percentage_rate':
                rec.unit_price_type = '%'
            else:
                rec.unit_price_type = ''

class CustomCalAppointments(models.Model):
    _inherit = ['calendar.appointment.type']

    apt_staff_list_ids = fields.One2many('staff.list.line', 'appointment_id', string='Staff Lines')

class ApptStaffPriceList(models.Model):
    _name = 'staff.list.line'
    _description = 'Staff List Line'

    appointment_id = fields.Many2one('calendar.appointment.type', string="Assign Staff")
    service_categ_id = fields.Many2one('appointment.category', string="Service Category")
    employee_id = fields.Many2one('hr.employee', string='Name',required=True)
    pay_rate_id = fields.Many2one('hr.employee.payrate', string='Pay rate ID')
    pay_type = fields.Selection([('no_pay','No Pay'),
                                   ('flat_rate','Flat Rate'),
                                   ('percentage_rate','Percentage Rate')], default='percentage_rate', string='Type Pay Rate')
    unit_price = fields.Float(string='Pay Rate')
    course_unit_price = fields.Float(string='Unit Price')
    unit_price_type = fields.Char(string=' ',compute='_compute_unit_price_type',store='True')
    time_id = fields.Many2one('time.time',string="Duration")
    duration = fields.Float(string='Duration', related='appointment_id.appointment_duration')

    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id:
                ytpe = self.env['hr.employee.payrate'].search([('employee_id', '=', rec.employee_id.id),('service_category_type_id', '=', rec.appointment_id.service_categ_id.id)],limit=1)
                if ytpe.staff_rate=='flat_rate':
                    pay_type = 'type_flat'
                elif ytpe.staff_rate=='percentage_rate':
                    pay_type = 'type_percentage'
                else:
                    pay_type = 'type_nopay'
                rec.pay_type=pay_type
                rec.unit_price=ytpe.staff_rate_percentage
        res = {'domain': {'employee_id': "[('id', 'not in', False)]"}}
        line_ids = []
        fac_id = self.env['hr.employee.category'].search([('name','=','Therapist')],limit=1)
        for line in self.env['hr.employee'].search([('employee_type','in',fac_id.id)]):
            line_ids.append(line.id)
        res['domain']['employee_id'] = "[('id', 'in', %s)]" % line_ids
        return res

    @api.depends('pay_type')
    def _compute_unit_price_type(self):
        for rec in self:
            if rec.pay_type=='type_flat':
                cur=self.env.company.currency_id.name
                rec.unit_price_type =cur
            elif rec.pay_type=='type_percentage':
                rec.unit_price_type = '%'
            else:
                rec.unit_price_type = ''

class CustomAppointmentsLine(models.Model):
    _inherit = ['appointment.line.id']

    therapist_id_rate = fields.Many2one('hr.employee.payrate', string='Therapist', copy=False)
