# -*- coding: utf-8 -*-
{
    'name': "PPTS Campaign Dashboard",
    'summary': """ """,
    'description': """ """,
    'author': "Hariprasanth",
    'website': "http://www.ppts.com",
    'category': 'CRM',
    'version': '0.1',
    'depends': ['base','web','ppts_my_practice'],
    'data': [
        'views/assets.xml',
        'views/campaign.xml',
    ],
    'qweb': [
        # "static/src/xml/tree.xml",
        "static/src/xml/campaign_view.xml",
    ]
}
