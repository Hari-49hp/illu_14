# -*- coding: utf-8 -*-
{
    'name' : 'PPTS : Security Configs',
    'version' : '14.0',
    'description': """Security Controls for Modules""",
    'category': 'crm',
    'website': 'http://www.pptssolutions.com',
    'author':'PPTS',
    'depends' : ['base'],
    'data': [
        'security/gobal_security.xml',
        # 'security/apt_group.xml',
        'views/website_menu.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
