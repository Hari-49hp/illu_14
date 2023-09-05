# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Custom Website',
    'version': '1.0.1',
    'category': 'Website',
    'sequence': 20,
    'summary': '',
    'description': "",
    'depends': ['website', 'sale', 'website_payment', 'website_mail', 'website_form', 'website_sale', 'digest'],
    'data': [
        'views/assets.xml',
        'views/cart.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.odoo.com/page/point-of-sale-shop',
    'external_dependencies': {"python" : ["numpy"]}
}
