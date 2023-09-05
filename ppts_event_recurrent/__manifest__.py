# -*- coding: utf-8 -*-
{
    'name': 'PPTS: Event Recurresion',
    'version': '1.0',
    'category': 'Event',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description':"""
                This module allows the user to attach survey in events and send mail based on button click
        """,
    'depends': ['base', 'event','survey', 'website_event_meet'],
    'data': [
            'security/ir.model.access.csv',
            'views/assets.xml',
            'views/event.xml',
            #'views/meeting_room.xml',
            'views/calendar.xml',
            'views/base_recurrent.xml',
    ],
    'qweb': ['static/src/xml/datepicker_widget.xml'],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
