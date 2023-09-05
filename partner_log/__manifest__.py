# -*- coding: utf-8 -*-
{
    'name': 'PPTS: Partner Log',
    'summary': 'Partner Based Log',
    'version': '14',
    'category': 'sale',
    'description': """
       Partner Based Log
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/log_config.xml',
        'views/mail_message.xml',
    ],
    'installable': True,
    'application':True,
    'active': False,
}


