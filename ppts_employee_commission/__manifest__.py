# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS Employee commission',
    'version': '1.0.1',
    'category': 'Sale',
    'sequence': 20,
    'summary': '',
    'description': "",
    'depends': ['base','hr','ppts_employee_availability','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_emloyee.xml',
        'views/pos_templates.xml',
        'wizard/employee_commission_report.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'qweb': [
        'static/src/xml/employee_popup.xml',
        'static/src/xml/employee.xml',
    ],
}
