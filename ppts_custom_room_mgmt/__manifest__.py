# -*- coding: utf-8 -*-
{
    'name': 'Custom Room Management',
    'summary': 'Custom Room Management',
    'version': '13',
    'category': 'events',
    'description': """
       Customizing Room Management, adding custom fields to get extra details of the room and Related Master. 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'event', 'website_event_meet',
                'mail',
                'ppts_custom_event_mgmt'],
    'data': [
        'security/ir.model.access.csv',
        'views/room_master.xml',
        'views/event_meeting_room.xml',
        # 'views/custom_calendar.xml',
        #'views/master.xml',

    ],
    'installable': True,
    'application':True,
    'active': False,
}


