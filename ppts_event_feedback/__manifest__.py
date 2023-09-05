# -*- coding: utf-8 -*-
{
    'name': 'Event Feedback',
    'version': '1.0',
    'category': 'Event',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description':"""
                This module allows the user to attach survey in events and send mail based on button click
        """,
    'depends': ['base', 'event','survey','ppts_custom_event_mgmt'],
    'data': [
           
            'views/event_inherit_view.xml',
        # 'reports/ppts_account_invoice_report.xml',
        # 'reports/ppts_account_invoice_report_templates.xml',

    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
