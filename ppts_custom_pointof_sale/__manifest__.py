{
    'name': "Point of Sale - Custom",
    'version': '1.1',
    'summary': """
        Changes on the PoS
       """,
    'description': """
        1. There is Order Ref generation based on the POS name and the daily sequence nos. We need to have one more Payment reference ID which should be Unique Sequence
        2. Under Order page in POS module, when we open the record, we see lot of incessant data… we need to limit those which is required. Others need to be removed
        3. We need to add Appointment ID to get the appointment details rather populating all the info here.
        4. Sales Rep need to be populated based on the Creation name
        5. After payment was made, we didn't see any kind of Accounting updates in the respective customer Ledget balance, Sales etc…. We need to check on that…
        6. Every payment we made, we need to have Payment ID
        7. Under Customer search, we need to list only Customers
        8. TIME STAMP is in different
        9. Auto Create Invoice need to be enabled
    """,
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': 'https://www.pptssolutions.com',
    'category': 'Point of Sale',
    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'ppts_custom_apt_mgmt', 'point_of_sale', 'product_return_pos', 'account_reports'],
    # View files
    'data': [
        'data/ir_sequence_data.xml',
        'views/pos_order_view.xml',
        'views/res_partner_view.xml',
        'views/pos_template.xml',
    ],
    'qweb': [
        'static/src/xml/ClientListScreen.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
