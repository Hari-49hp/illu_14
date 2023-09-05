# -*- coding: utf-8 -*-
{
    'name': "PPTS: POS Event Management",
    'summary': """  """,
    'description': """  """,
    'author': "Hariprasanth.N",
    'website': "http://www.ppts.com",
    'category': 'Point of Sale',
    'version': '0.1',
    'depends': ['base', 'web', 'point_of_sale', 'event', 'sale', 'sale_management','ppts_custom_event_mgmt','event_sale','custom_event_mail', 'event'],
    'data': [
        'security/ir.model.access.csv',
        'data/event_gift_template.xml',
        'wizard/event_payment_view.xml',
        'views/res_config.xml',
        'views/event_registration_view.xml',
        'views/event_sale_pos.xml',
        'views/pos_order.xml',

    ],
}
