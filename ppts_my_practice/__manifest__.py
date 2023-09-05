# -*- coding: utf-8 -*-
{
    'name': 'PPTS: My Practice',
    'version': '14.0',
    'category': 'events',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description': """
                 PPTS: My Practice
        """,
    'depends': ['base', 'account_accountant', 'account', 'account_reports',
                'ppts_custom_apt_mgmt','crm', 'event', 
                'ppts_employee_availability', 'asterisk_calls','ppts_event_registration_view'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/dashboard_view.xml',
        'views/my_practice_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
