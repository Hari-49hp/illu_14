# -*- coding: utf-8 -*-
{
    'name': 'PPTS: Backend Theme',
    'version': '1.0',
    'category': "Themes/Backend",
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description':"""
                This module allows the user to attach survey in events and send mail based on button click
        """,
    'depends': ['base', 'web_editor', 'web_enterprise','web'],
    "qweb": [
        "static/src/xml/appsbar.xml",
    ],
    'data': [
        "views/assets.xml"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
