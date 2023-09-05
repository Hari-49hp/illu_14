# -*- coding: utf-8 -*-
{
    'name': "PPTS: Bulk Payment",
    'summary': """   """,
    'description': """   """,
    'author': "Hariprasanth.N",
    'website': "http://www.ppts.com",
    'category': 'Payment',
    'version': '0.1',
    'depends': ['base','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'wizard/bulk_payment.xml',
    ],
}
