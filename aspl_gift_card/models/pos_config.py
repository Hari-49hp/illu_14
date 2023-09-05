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

from odoo import models, fields, api


class POSConfig(models.Model):
    _inherit = 'pos.config'

    enable_gift_card = fields.Boolean('Gift Card')
    gift_card_account_id = fields.Many2one('account.account', string="Gift Card Account")
    gift_card_product_id = fields.Many2one('product.product', string="Gift Card Product")
    enable_journal_id = fields.Many2one('pos.payment.method', string="Enable Journal")
    manual_card_number = fields.Boolean('Manual Card No.')
    msg_before_card_pay = fields.Boolean('Confirm Message Before Card Payment')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

