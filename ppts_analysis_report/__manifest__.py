# -*- coding: utf-8 -*-
{
    'name': 'PPTS: Report',
    'version': '14.0',
    'category': 'Reports',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'description': """
                 PPTS: Analysis Report
        """,
    'depends': ['base', 'account_accountant', 'account', 'account_reports', 'ppts_custom_apt_mgmt','point_of_sale','event'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/sales_report_summary_view.xml',
        #'views/sales_report_filter.xml',
        'views/sales_by_service_view.xml',
        'views/sales_by_category_view.xml',
        'views/sales_by_rep_view.xml',
        'views/invoice_report_view.xml',
        'views/sales_by_product_view.xml',
        'views/voided_sales_view.xml',
        'views/sales_tax_view.xml',
        'views/inherit_pos_view.xml',
        'views/attendance_revenue_view.xml',
        'views/best_sellers_view.xml',
        'views/returns_view.xml',
        'wizard/report_wizard_view.xml',
        'wizard/service_wizard_view.xml',
        'wizard/rep_wizard_view.xml',
        'wizard/product_wizard_view.xml',
        'wizard/voided_wizard_view.xml',
        'wizard/taxes_wizard_view.xml',
        'wizard/best_sellers_wizard_view.xml',
        'wizard/attendance_revenue_wizard_view.xml',
        'wizard/category_wizard_view.xml',
        'wizard/invoice_wizard_view.xml',
        'wizard/returns_wizard_view.xml',
        'views/report_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
