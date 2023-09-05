# -*- coding: utf-8 -*-
{
    'name': 'PPTS: Pay Rate',
    'version': '1.0',
    'category': 'Event',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description':"""
                This module allows the user to configurePay rates for employees and it can be linked with appointments and events. Separate report also added to take Pay Rate report appointments and Events wise. 
        """,
    'depends': ['base', 'event', 'hr','website_calendar','ppts_custom_apt_mgmt','ppts_custom_event_mgmt'],
    'data': [
            'security/ir.model.access.csv',
            'views/employee.xml',
            'views/event_event.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
