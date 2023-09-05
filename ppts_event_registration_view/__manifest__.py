# -*- coding: utf-8 -*-
{
    'name': 'Event Registration View',
    'version': '1.0',
    'category': 'Event',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description':"""
                This module allows the user to client Registration View
        """,
    'depends': ['base', 'event','ppts_custom_room_mgmt','ppts_custom_event_mgmt'],
    'data': [
           
            'views/event_inherit_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
