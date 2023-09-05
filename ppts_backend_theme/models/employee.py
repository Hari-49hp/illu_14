from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pay_rate_ids = fields.One2many('hr.employee.payrate','employee_id',string='Pay Rate')

class HrEmployeePayrate(models.Model):
    _name = 'hr.employee.payrate'
    # _rec_name = 'selected_date'
    service_category_type_id = fields.Many2one('appointment.category','Service Category')
    appoinment_type_id = fields.Many2one('calendar.appointment.type','Appointment')
    length = fields.Integer('Length mins')
    staff_rate = fields.Selection([('no_pay','No Pay'),('flat_rate','Flat Rate'),('percentage_rate','Percentage Rate')],string='Staff Pay Rate', default='no_pay')
    staff_rate_percentage = fields.Integer('%')
    employee_id = fields.Many2one('hr.employee',string='Employee')