# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Custom Point of Sale',
    'version': '1.0.1',
    'category': 'Sales/Point Of Sale',
    'sequence': 20,
    'summary': 'Custom User-friendly PoS interface for shops and restaurants',
    'description': "",
    'depends': ['point_of_sale','ppts_custom_apt_mgmt','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/pos_config.xml',
        'views/pos_order.xml',
        'views/pos_return_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'qweb': ['static/src/xml/pos_loading_screen.xml',
             'static/src/xml/MyCenter.xml',
             'static/src/xml/Screens/ProductScreen.xml',
             ],
    'website': 'https://www.odoo.com/page/point-of-sale-shop',
}
