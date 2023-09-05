# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Universal Partner Search',
    'version': '1.0.1',
    'category': 'Base',
    'sequence': 20,
    'summary': ' ',
    'description': "",
    'depends': ['base','web'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/assets.xml',
        # 'views/pos_config.xml',
        # 'views/pos_order.xml',
        'views/assets.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'qweb': [
            'static/src/xml/control_panel.xml',
        ],
    'website': 'https://www.odoo.com/page/point-of-sale-shop',
}