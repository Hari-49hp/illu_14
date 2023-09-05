# -*- coding: utf-8 -*-

{
    'name': 'PPTS: Whatsapp Integration',
    'version': '13.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'category': 'base',
    'depends': ['base','web','mass_mailing'],
    'data': [
        'security/ir.model.access.csv',
        'views/watsapp_template.xml',
        'views/mailing.xml',
        'views/res_config.xml',
        'views/assets.xml',
    ],
    'qweb': ["static/src/xml/*.xml"],
    'installable': True,
    'application': True,
    'auto_install': False,
}
