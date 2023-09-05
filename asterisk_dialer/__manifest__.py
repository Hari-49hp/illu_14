# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
# -*- coding: utf-8 -*-
{
    'name': "Aterisk Dialer",
    'summary': """
        Dialer Software""",
    'description': """
    """,
    'price': 250.0,
    'currency': 'EUR',
    'maintainer': 'Odooist',
    'support': 'odooist@gmail.com',
    'license': 'OPL-1',
    'category': 'Phone',
    'author': "Odooist",
    'version': '1.1',
    'depends': ['asterisk_common','crm','event','utm','ppts_custom_event_mgmt','sale_crm', 'custom_crm' ,'ppts_custom_apt_mgmt'],
    'data': [
        # Security
        'security/groups.xml',
        'security/user/user_model_access.xml',
        'security/user/user_record_rules.xml',
        'security/admin_model_access.xml',
        'security/agent_model_access.xml',
        # Wizards
        'wizards/generate_contacts_views.xml',
        'wizards/add_contacts.xml',
        'wizards/data_miner.xml',
        'wizards/call_feedback_view.xml',
        # Data
        'data/events.xml',
        'data/campaign_type.xml',
        # Views
        'views/menus.xml',
        'views/operator.xml',
        'views/channel.xml',
        'views/resources.xml',
        'views/contact.xml',
        'views/campaign_type_view.xml',
        'views/campaign.xml',
        'views/campaign_log.xml',
        'views/ir_cron.xml',
        'views/settings.xml',
        'views/campaign_crm.xml',
        'views/crm_stage_view.xml',
        'views/partner.xml',
    ],
    'js': ['static/src/js/*.js'],
    'css': [],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/campaign.png'],
}
