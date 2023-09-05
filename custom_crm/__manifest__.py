# -*- coding: utf-8 -*-
{
    'name': 'Custom CRM',
    'summary': 'Custom CRM',
    'version': '13',
    'category': 'sale',
    'description': """
       Customizing CRM Opportunity and Lead, adding custom fields to get extra details of the customer. 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'crm' , 'sale', 'sale_management', 'mail','account','partner_firstname','event'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'data/ir_sequence.xml',
        'views/custom_crm.xml',
        'views/master.xml',
        'data/online_demo_data.xml',
        'data/branch_demo_data.xml',
        'data/visit_demo_data.xml',
        'data/about_demo_data.xml',
        'data/interested_demo_data.xml',
        'data/struggling_demo_data.xml',
        'data/holistic_demo_data.xml',
        'data/membership_demo_data.xml',
        # 'data/event_reg_lead_template.xml'
    ],
    'installable': True,
    'application':True,
    'active': False,
}


