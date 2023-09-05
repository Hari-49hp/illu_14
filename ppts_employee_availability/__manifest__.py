# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Availability',
    'version': '1.0.1',
    'category': 'Event',
    'sequence': 20,
    'summary': '',
    'description': "",
    'depends': ['base','web','event','sale', 'hr',
                # 'ppts_custom_event_mgmt',
                # 'ppts_custom_apt_mgmt',
                'ppts_custom_room_mgmt', 
                'sale_order_line',
                'web_widget_datepicker_options'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/employee_sequence.xml',
        'views/availability.xml',
        'views/hr.xml',
        'wizard/wizard.xml',
    ],
    "qweb": ["static/src/xml/base.xml"],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
