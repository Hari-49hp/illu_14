# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS: Custom Appointments Notification',
    'version': '1.0.1',
    'category': 'Event',
    'sequence': 20,
    'summary': '',
    'description': "",
    'depends': ['base','website','ppts_custom_apt_mgmt','event','mass_mailing',
                'sale','website_mail','website_form', 'digest','website_event',
                'hr','base_setup','contacts'],
    'data': [
        # 'edi/appt_allocation_checklist_mail.xml',
        'security/ir.model.access.csv',
        'edi/appt_cancel_mail.xml',
        'edi/appt_confirmation_mail.xml',
        'edi/appt_rescheduled_mail.xml',
        'edi/appt_thanks_mail.xml',
        'edi/appt_reminder_mail.xml',
        'data/ir_cron.xml',
        # 'views/custom_appointments.xml',
        'views/template_configuration.xml',
        
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.odoo.com/page/point-of-sale-shop',
}
