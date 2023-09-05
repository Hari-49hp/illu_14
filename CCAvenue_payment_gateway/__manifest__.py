# -*- coding: utf-8 -*-
###################################################################################
#
#
###################################################################################

{
    'name': 'ODOO CCAvenue Payment Gateway',
    'version': '14.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'CCAvenue Payment Gateway Integration for Odoo 14',
    'description': 'CCAvenue Payment Gateway Integration for Odoo 14',
    'author': 'PPTS',
    'website': 'www.pptssolutions.com',
    #     'images': ['static/description/banner.gif'],
    'depends': ['payment','website_sale'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/assets.xml',
        'data/data.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}

    # Add below line to base view
    
#      <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.2/rollups/aes.js"></script>
#
#      <?xml version="1.0"?>
#     <t name="Sidebar" t-name="portal.portal_sidebar">
#             <t t-call="portal.portal_layout">
#                 <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.2/rollups/aes.js"></script>
#                 <body data-spy="scroll" data-target=".navspy" data-offset="50">
#                     <div class="container o_portal_sidebar"/>
#                     <div class="oe_structure mb32" id="oe_structure_portal_sidebar_1"/>
#                 </body>
#             </t>
#         </t>
#
#         <?xml version="1.0"?>
# <t name="Payment" t-name="website_sale.payment">
#         <t t-call="website.layout">
#
#             <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.2/rollups/aes.js"></script>
#
#             <t t-set="additional_title">Shop - Select Payment Acquirer</t>
#             <t t-set="no_footer" t-value="1"/>


# <?xml version="1.0"?>
# <t t-name="payment.pay">
#         <t t-call="portal.frontend_layout">
#             <script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/3.1.2/rollups/aes.js"></script>
#             <t t-set="additional_title">Payment</t>



