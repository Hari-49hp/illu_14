# -*- coding: utf-8 -*-
{
    'name': 'Custom Appointments Management',
    'summary': 'Custom Appointments & Booking',
    'version': '14',
    'category': 'events',
    'description': """
       Customizing Appointments & Booking management, adding custom fields to get extra details of the Appointments & Booking and Related Master. 
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'depends': ['base', 'sale', 'sales_team','contacts','mass_mailing','mail','calendar','hr', 'event',
                'website_calendar',
                'ppts_employee_availability',
                'ppts_custom_event_mgmt',
                'ppts_custom_room_mgmt',
                'ppts_modules_addon',
                'account','sale_coupon','coupon',
                'point_of_sale',
                'pos_credit_payment',
                'product',
                'bi_sale_delivery_invoice_status',
                'date_highlighter_widget',
                ],
    
    'data': [
        'security/ir.model.access.csv',
        'security/user_groups.xml',
        'data/ir_rule.xml',
        'data/booking_sequence.xml',
        'data/appointments_so_sequence.xml',
        'data/appointment_mail.xml',
        'views/custom_appointments_view.xml',
        'views/time.xml',
        'views/pos.xml',
        'views/sale.xml',
        'views/custom_apt_master_view.xml',
        'views/custom_apt_package_master_view.xml',
        'views/custom_apt_pricing_view.xml',
        'views/custom_appointments_type_view.xml',
        'views/res_partner.xml',
        'views/custom_calendar.xml',
        # 'views/custom_apt_meeting_room.xml',
        'views/custom_apt_promo.xml',
        'views/apt_single.xml',
        'views/hr_employee.xml',
        'views/tag_by.xml',
        'views/payment.xml',
        'views/assets.xml',
        'views/custom_appointments_filter.xml',
        'views/custom_appointments_report_filter.xml',
        'views/availability_view.xml',
        'wizard/wizard_single_service.xml',
        'wizard/apt_retail_wizard.xml',
        'views/event_view.xml',
        
        'reports/proforma_invoice_report.xml',
        'reports/proforma_invoice_template.xml',

    ],
    'qweb': [
                "static/src/xml/button_save.xml",
            ],
    'installable': True,
    'application':True,
    'active': False, 
}

