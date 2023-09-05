# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Custom Partner',
    'version': '14',
    'category': 'Event',
    'sequence': 20,
    'summary': '',
    'description': "",
    'depends': ['base','contacts','event','sale','ppts_custom_apt_mgmt', 'ppts_custom_pointof_sale', 
                'partner_log','pos_event_management', 'web_tree_dynamic_colored_field','sign','ppts_website_theme'],
    'data': [
        'security/ir.model.access.csv',
        'data/sign_mail_template.xml',
        'views/assets.xml',
        'views/partner.xml',
        'views/history.xml',
    ],
    'qweb': [
        'static/src/xml/phone_call_dialler.xml',
        
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'website': 'https://www.odoo.com/page/point-of-sale-shop',
}
