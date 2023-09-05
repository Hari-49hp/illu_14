# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': "POS Gift Card (Community)",
    'summary': "This module allows user to purchase giftcard, use giftcard and also recharge giftcard.",
    'description': """
        User can purchase giftcard, use giftcard and also recharge giftcard. 
    """,
    'category': 'Point of Sale',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': "http://www.acespritech.com",
    'version': '1.1',
    'depends': ['base', 'point_of_sale'],
    'price': 26,
    'currency': 'EUR',
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'views/pos_config_view.xml',
        'views/pos_assets.xml',
        'views/pos_payment_method_view.xml',
        'views/gift_card.xml',
    ],
    'qweb': [
        'static/src/xml/Screens/ProductScreen/ControlButtons/giftCardControlButton.xml',
        'static/src/xml/Screens/GiftCardScreen/GiftCardScreen.xml',
        'static/src/xml/Screens/GiftCardScreen/GiftCardLine.xml',
        'static/src/xml/Screens/GiftCardScreen/giftCardCreateScreen.xml',
        'static/src/xml/Popups/giftCardCreatePopupConform.xml',
        'static/src/xml/Popups/giftCardRedeemPopup.xml',
        'static/src/xml/Popups/giftCardEditExpirePopup.xml',
        'static/src/xml/Popups/giftCardExchangePopup.xml',
        'static/src/xml/Popups/giftCardRechargePopup.xml',
        'static/src/xml/Screens/PaymentScreen/PaymentScreen.xml',
        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    "installable": True,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
