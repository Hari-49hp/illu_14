# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Custom Point of Sale Loyalty',
    'version': '1.0.2',
    'category': 'Sales/Point Of Sale',
    'sequence': 21,
    'summary': 'Custom User-friendly PoS Loyalty interface for shops and restaurants',
    'description': "",
    'depends': ['pos_loyalty'],
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'qweb': [
            'static/src/xml/Screens/RewardButton.xml',
             ],
    'website': '',
}
