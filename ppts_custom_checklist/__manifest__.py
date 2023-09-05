# -*- coding: utf-8 -*-
{
    'name': 'PPTS Custom Checklist',
    'summary': 'PPTS Custom Checklist',
    'version': '13',
    'category': 'event',
    'description': """
       Customizing event, adding custom fields.
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['event','project','ppts_custom_event_mgmt','ppts_custom_room_mgmt','ppts_custom_apt_mgmt'],
    'data': [
        'security/ir.model.access.csv',
        'views/master.xml',
        'wizard/checklist_wizard_view.xml',
        'wizard/class_checklist_wizard_view.xml',
        'views/project.xml',
        'views/event_view.xml',
        'views/event_class_view.xml',
    ],
    'installable': True,
    'application':True,
    'active': False,
}


