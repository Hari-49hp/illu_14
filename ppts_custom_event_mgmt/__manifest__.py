# -*- coding: utf-8 -*-
{
    'name': 'Custom Event Management',
    'summary': 'Custom Event Management',
    'version': '14',
    'category': 'events',
    'description': """
       Customizing Event Management, adding custom fields to get extra details of the events and Related Master. 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'event','calendar','hr','mass_mailing','ppts_modules_addon','website_event','event_sale'],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'reports/proforma_invoice_report.xml',
        'reports/proforma_invoice_template.xml',
        'data/event_sequence.xml',
        'data/event_approver_template.xml',
        'data/event_mail_template.xml',
        'views/event_source_view.xml',
        'views/custom_event.xml',
        'views/custom_event_master.xml',
        'views/custom_calendar.xml',
        'views/event_parking.xml',
        'views/custom_event_class.xml',
        'views/custom_employee.xml',
        # 'views/custom_event_view.xml',
        'views/event_reschedule.xml',
        'views/custom_event_filters.xml',
        'views/custom_event_end_cron.xml',
        'views/custom_event_sale_coupon.xml',
        'views/event_multidate.xml',
        'views/custom_event_form_view.xml',
        'views/custom_event_ticket.xml',
        'views/event_payment_views.xml',
        'wizard/multidate_wizard_view.xml',
        'wizard/event_cancellation_views.xml',
        'wizard/event_reject_views.xml',
        'wizard/event_payment_views.xml',
        # 'wizard/image_wizard_view.xml',

    ],
    'installable': True,
    'application':True,
    'active': False,
}


