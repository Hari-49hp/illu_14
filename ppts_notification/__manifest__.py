# -*- coding: utf-8 -*-
{
    'name': "PPTS: Notification",
    'summary': """ Notification """,
    'description': """ Notification """,
    'author': "Hariprasanth.n",
    'website': "http://www.ppts.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','mass_mailing','website_mass_mailing'],
    'data': [
        'security/ir.model.access.csv',
        'views/mailing_contact.xml',
        'views/mailing_list.xml',
        'wizard/mailing_contact.xml',
    ],
}
