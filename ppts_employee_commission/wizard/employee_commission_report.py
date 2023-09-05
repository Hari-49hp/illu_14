# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields, _
import xlwt
import base64
from io import BytesIO

class EmployeeCommissionReport(models.TransientModel):
    _name = "employee.commission.report"

    date_from = fields.Date(string='Date From', default=lambda *a: fields.Date.today() + relativedelta(day=1), required=True)
    date_to = fields.Date(string='Date To', default=lambda *a: fields.Date.today() + relativedelta(day=1, months=+1, days=-1), required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    product_ids = fields.Many2many('product.product', string='Product')
    filename = fields.Char(string='File Name', size=64)
    excel_file = fields.Binary(string='Report File')

    def print_commission_xls_report(self):
        employee_ids = self.employee_ids if self.employee_ids else self.env['hr.employee'].search([])
        
        file_name = 'Employee Commission Report.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'
        format0 = xlwt.easyxf('align: horiz center;font: name Calibri; borders:left thin, right thin, top thin, bottom thin;')
        format1 = xlwt.easyxf('align: horiz center;font:name Calibri,bold True; borders:left thin, right thin, top thick;')
        format2 = xlwt.easyxf('align: horiz left;font: name Calibri; borders:left thin, right thin, top thin, bottom thin;')
        format3 = xlwt.easyxf('align: horiz right;font: name Calibri; borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
        format4 = xlwt.easyxf('align: horiz center;font: name Calibri; borders:left thin, right thin, top thin, bottom thin;', num_format_str='dd/mm/yyyy')
        format5 = xlwt.easyxf('align: horiz center;font: name Calibri; borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
        
        for emp in employee_ids:
            domain = [('order_id.pos_order_date', '>=', self.date_from),('order_id.pos_order_date', '<=', self.date_to),('hr_employee_id', '=', emp.id),]
            if self.product_ids:
                domain.append(('product_id', 'in', self.product_ids.ids), )
            pos_lines = self.env['pos.order.line'].search(domain, order='id desc')
            
            sheet = workbook.add_sheet(emp.name, cell_overwrite_ok=True)
            
            for i in range(1,9):
                sheet.col(i).width = int(20*250)
            sheet.write(0, 0, 'Item no', format1)
            sheet.write(0, 1, 'Order Ref', format1)
            sheet.write(0, 2, 'Order Date', format1)
            sheet.write(0, 3, 'Employee Name', format1)
            sheet.write(0, 4, 'Product name', format1)
            sheet.write(0, 5, 'Qty', format1)
            sheet.write(0, 6, 'Price total', format1)
            sheet.write(0, 7, 'Commission %', format1)
            sheet.write(0, 8, 'Commission Amount', format1)
            r=1;tot=0;
            for line in pos_lines:
                sheet.write(r, 0, r, format0)
                sheet.write(r, 1, line.order_id.name, format0)
                sheet.write(r, 2, line.order_id.pos_order_date, format4)
                sheet.write(r, 3, line.hr_employee_id.name, format2)
                sheet.write(r, 4, line.product_id.name, format2)
                sheet.write(r, 5, line.qty, format5)
                sheet.write(r, 6, line.price_subtotal, format3)
                sheet.write(r, 7, line.commission_percentage, format3)
                sheet.write(r, 8, line.commission_amt, format3)
                tot+=line.commission_amt
                r+=1
            sheet.write(r, 8, tot, format3)
        fp = BytesIO()
        workbook.save(fp)
        self.write({'filename': fp, 'excel_file': base64.encodestring(fp.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=employee.commission.report&field=excel_file&download=true&id=%s&filename=%s' % (self.id, file_name),
            'target': 'new',
        } 
        