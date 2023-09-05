# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Custom Employee',
    'version': '1.0.1',
    'category': 'Appointment',
    'sequence': 20,
    'summary': '',
    'description': "",
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr.xml',
        'views/support.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
