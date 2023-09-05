# -*- coding: utf-8 -*-
###################################################################################
#
#
###################################################################################


from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from datetime import datetime
from werkzeug import urls
import json
import requests
from odoo.http import request
import logging
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
import re

_logger = logging.getLogger(__name__)


class PaymentToken(models.Model):
    _inherit = 'payment.token'
    
    
    cc_avenue_number = fields.Char('Card Number')
    cc_avenue_cvc = fields.Char('CVC')
    cc_avenue_expiry = fields.Char('Expiry Date')
    cc_avenue_name = fields.Char('Card Holder Name')
    cc_avenue_card_type = fields.Char('Card Type')
    

class PaymentAcquirerCCAvenue(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('CCAvenue', 'CCAvenue')], ondelete={'CCAvenue': 'set default'})
    CCAvenue_merchant_key = fields.Char('Merchant Key', required_if_provider='CCAvenue',
                                        groups='base.group_user')
    CCAvenue_access_code = fields.Char('Merchant Access Code', required_if_provider='CCAvenue',
                                        groups='base.group_user')
    CCAvenue_encryption_key = fields.Char('Encryption Key', required_if_provider='CCAvenue',
                                        groups='base.group_user')
    
        
    def _get_CCAvenue_urls(self, environment):
        """ CCAvenue URLs"""
        if environment == 'prod':
            return 'https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction'
        return 'https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction'
    
    def CCAvenue_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_CCAvenue_urls(environment)

    def CCAvenue_form_generate_values(self ,values):
        # get the sale order
        order_id = values.get('reference').split('-')[0]
        sale_id = self.env['sale.order'].sudo().search([('name','ilike',order_id)],limit=1)
        # end
        print(request.session)
        CCAvenue_bank_id = False
        expiry_month = ""
        expiry_year = ""
        cc_number = ""
        cc_cvc = ""
        cc_holder_name = ""
        card_type = ""
        
        try:
            
            if request.session.get("CCAvenue_bank_id", False):
                CCAvenue_bank_id = request.session.get("CCAvenue_bank_id", False)
                cc_number = request.session.get("cc_number", False)
                cc_cvc = request.session.get("cc_cvc", False)
                if request.session.get("cc_expiry", False):
                    expiry_month = request.session.get("cc_expiry", False).split('/')[0]
                    expiry_year = request.session.get("cc_expiry", False).split('/')[1]
                cc_holder_name = request.session.get("cc_holder_name", False)
                cc_brand = request.session.get("cc_brand", False)
                
            if request.session.get("ccavenue_save_token", False) == "on" and request.session.get("CCAvenue_bank_id", False) == 'OPTCRDC':
                card_type = "CRDC"
                if cc_number:
                    pm_id = self.env['payment.token'].sudo().search(([('cc_avenue_number','=',cc_number),('acquirer_id','=',self.id),('partner_id','=',int(values ['billing_partner_id'])),('cc_avenue_card_type','=',request.session.get("CCAvenue_bank_id", False))]), limit=1)
                    
                    card_values = {
                        'cc_avenue_number': cc_number,
                        'cc_avenue_cvc': cc_cvc,
                        'cc_avenue_name': cc_holder_name,
                        'cc_avenue_expiry': request.session.get("cc_expiry", False),
                        'acquirer_id': self.id,
                        'acquirer_ref': self.name,
                        'partner_id': int(values ['billing_partner_id']),
                        'cc_avenue_card_type': request.session.get("CCAvenue_bank_id", False),
                    }
                    print(card_values)
                    if not pm_id:
                        pm_id = self.env['payment.token'].sudo().create(card_values)
                    else:
                        pm_id.write(card_values)
        except Exception as e:
            
            _logger.info(str(e))
            
                    
                
            
            
            
        self.ensure_one ()
        base_url=self.env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
        base_url="https://illuminations.pptssolutions.com"
        now=datetime.now ()
        payment_option = CCAvenue_bank_id
        
        partner_id = self.env['res.partner'].sudo().browse(values ['partner_id'])
        
        billing_partner_state = billing_partner_email = billing_partner_phone = billing_partner_country = billing_partner_zip = billing_partner_city = billing_partner_address = billing_partner_name = language = currency = ""
        
        if values.get('currency', False):
            currency = values ['currency'].name
            
        if values.get('partner_lang', False):
            lang_id = self.env['res.lang'].sudo().search([('code','=',values.get('partner_lang', False))])
            if lang_id:
                language = lang_id.iso_code
        
        if values.get('billing_partner_name', values.get('partner_name', False)):
            # billing_partner_name = values.get('billing_partner_name', values.get('partner_name', False))
            billing_partner_name = sale_id.customer_id.name

        if values.get('billing_partner_address', False):
            # billing_partner_address = values ['billing_partner_address']
            billing_partner_address = sale_id.customer_id.street

        if values.get('billing_partner_city', False):
            # billing_partner_city = values ['billing_partner_city']
            billing_partner_city = sale_id.customer_id.city_id.name

        # if values.get('billing_partner_state', False):
        #     # billing_partner_state = values ['billing_partner_state'].name
        #     billing_partner_state = sale_id.customer_id.state_id.name or False

        # if values.get('billing_partner_zip', False):
        #     billing_partner_zip = values ['billing_partner_zip']
        #     # billing_partner_zip = sale_id.customer_id.zip

        if values.get('billing_partner_country', False):
            # billing_partner_country = values ['billing_partner_country'].name
            billing_partner_country = sale_id.customer_id.country_id.name

        # if values.get('billing_partner_phone', False):
        #     # billing_partner_phone = values ['billing_partner_phone']
        #     billing_partner_phone = sale_id.customer_id.mobile

        if values.get('billing_partner_email', False):
            # billing_partner_email = values ['billing_partner_email']
            billing_partner_email = sale_id.customer_id.email
        billing_partner_phone = sale_id.customer_id.mobile

        merchant_data='merchant_id='+self.CCAvenue_merchant_key+'&'+'order_id='+values ['reference'] + '&' + "currency=" + currency + '&' + 'amount=' + str(values ['amount'])+'&'+\
            'payment_option='+payment_option +'&'+\
            'redirect_url='+urls.url_join (base_url ,'/payment/CCAvenue/return/')+'&'+'cancel_url='+urls.url_join (base_url ,'/payment/CCAvenue/cancel/')+'&'+'language='+language+'&'+'billing_name='+billing_partner_name+'&'+\
            'billing_address='+billing_partner_address+'&'+'billing_city='+billing_partner_city+'&'+'billing_state='+billing_partner_state+'&'+\
            'billing_zip='+billing_partner_zip+'&'+'billing_country='+billing_partner_country+'&'+'billing_tel='+billing_partner_phone+'&'+\
            'billing_email='+billing_partner_email+'&'+'delivery_name='+""+'&'+'delivery_address='+""+'&'+\
            'delivery_city='+""+'&'+'delivery_state='+""+'&'+'delivery_zip='+""+'&'+\
            'delivery_country='+""+'&'+'delivery_tel='+""+'&'+'merchant_param1='+""+'&'+\
            'merchant_param2='+""+'&'+'merchant_param3='+""+'&'+'merchant_param4='+""+'&'+\
            'merchant_param5='+""+'&'+'promo_code='+""+'&'
            
            # 'card_number='+cc_number+'&'+'expiry_month='+expiry_month+'&'+'expiry_year='+expiry_year+'&'+\
            #'cvv_number='+cc_cvc+'&'+'card_name='+cc_holder_name+'&'+'card_type='+card_type+'&'+\
            
        encrypttext = self.encrypt(merchant_data, self.CCAvenue_encryption_key)
        
        
        CCAvenue_values=dict (
            
            tx_url="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction",
            p_merchant_id=self.CCAvenue_merchant_key ,
            p_CCAvenue_access_code=self.CCAvenue_access_code ,
            p_CCAvenue_encryption_key=self.CCAvenue_encryption_key ,
            
            payment_option = CCAvenue_bank_id,
            p_order_id=str(values ['reference']) ,
            p_currency=currency or 'AED' ,
            p_amount="%s" % values ['amount'] ,
            p_redirect_url=urls.url_join (base_url ,'/payment/CCAvenue/return/') ,
            p_cancel_url=urls.url_join (base_url ,'/payment/CCAvenue/cancel/') ,
            p_language=language ,
            
            card_number =cc_number,
            expiry_month =expiry_month,
            expiry_year =expiry_year,
            cc_cvc =cc_cvc,
            card_name =cc_holder_name,
            card_type =card_type,
            
            p_billing_name=billing_partner_name ,
            p_billing_address=billing_partner_address ,
            p_billing_city=billing_partner_city ,
            p_billing_state=billing_partner_state ,
            p_billing_zip=billing_partner_zip ,
            p_billing_country=billing_partner_country ,
            p_billing_tel=billing_partner_phone ,
            p_billing_email=billing_partner_email ,
            
            p_delivery_name="" ,
            p_delivery_address="" ,
            p_delivery_city="" ,
            p_delivery_state="" ,
            p_delivery_zip="" ,
            p_delivery_country="" ,
            p_delivery_tel="" ,
            
            p_merchant_param1="" ,
            p_merchant_param2="" ,
            p_merchant_param3="" ,
            p_merchant_param4="" ,
            p_merchant_param5="" ,
            p_promo_code="" ,
            encRequest=encrypttext ,
            
            )
        
        
        return CCAvenue_values
    
    def pad(self, data):
        length = 16 - (len(data) % 16)
        data += chr(length)*length
        return data
    
    def encrypt(self, plainText,workingKey):
        iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        plainText = self.pad(plainText)
        workingKey =  hashlib.md5(workingKey.encode("utf-8")).digest()
        cipher = AES.new(workingKey, AES.MODE_CBC, iv)
        encryptedText = cipher.encrypt(plainText.encode("utf-8")).hex()
        print(encryptedText)
        return encryptedText 
    
    def decrypt(self, cipherText):
        iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    
        decDigest = hashlib.md5()
        decDigest.update(self.CCAvenue_encryption_key.encode())
        encryptedText = bytes.fromhex(cipherText)
        dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
        decryptedText = dec_cipher.decrypt(encryptedText).decode("utf-8")
        
        params = re.findall(r'([^=&]+)=([^=&]+)', decryptedText)
        res = dict()
        for key, val in params:
            res.setdefault(key, []).append(val)
            
            
        return res
    
    
    # Function to convert  
    def listToString(self, value): 
        
        # initialize an empty string
        str1 = "" 
        
        # traverse in the string  
        for ele in value: 
            str1 += ele  
        
        # return string  
        return str1 
            
    
    

class PaymentTransactionAtom(models.Model):
    _inherit = 'payment.transaction'

    CCAvenue_txn_type = fields.Char('Transaction type')
    

    @api.model
    def _CCAvenue_form_get_tx_from_data(self ,data):
        """ Given a data dict coming from CCAvenue, verify it and find the related
        transaction record. """
        """
        {'order_id': ['S00037-32'], 'tracking_id': ['110023230726'], 'bank_ref_no': ['null'], 'order_status': ['Aborted'], 
        'payment_mode': ['Credit Card'], 'card_name': ['null'], 'status_message': ['I wish to review my order again before completing the transaction.'],
         'currency': ['USD'], 'amount': ['750.0'], 'billing_name': ['Mitchell Admin'], 'billing_address': ['215 Vine St'], 
         'billing_city': ['Scranton'], 'billing_state': ['Pennsylvania'], 'billing_zip': ['18503'], 
         'billing_country': ['United States'], 'billing_tel': ['1 555-555-5555'], 'billing_email': ['admin@yourcompany.example.com'], 'vault': ['N'],
          'offer_type': ['null'], 'offer_code': ['null'], 'discount_value': ['0.0'], 'mer_amount': ['750.0'], 'bank_qsi_no': ['null'],
           'bank_receipt_no': ['null\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b']}
         
         """
         
        acquirer_id = data.get("acquirer_id", False)
        
        
        
        reference, txnid = data.get('order_id')[0], data.get('tracking_id')[0]
        
        if not reference or not txnid:
            raise ValidationError(_('CCAvenue: received data with missing reference (%s) or transaction id (%s)') % (reference, txnid))
        
        transaction=self.env ['payment.transaction'].sudo().search ([('reference' ,'=' ,reference)])
        
        if not transaction:
            error_msg = (_('CCAvenue: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (_('CCAvenue: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)
        
        return transaction
    
    def _CCAvenue_form_get_invalid_parameters(self ,data):
        invalid_parameters = []
#         if self.acquirer_reference and data.get('TransactionId') != self.acquirer_reference:
#             invalid_parameters.append(('Reference code', data.get('TransactionId'), self.acquirer_reference))
        _logger.info('CCAvenue invalid_parameters' % (invalid_parameters))
        return invalid_parameters
    
    def _CCAvenue_form_validate(self, data):
        # Response
        """
        {'order_id': ['S00037-32'], 'tracking_id': ['110023230726'], 'bank_ref_no': ['null'], 'order_status': ['Aborted'], 
        'payment_mode': ['Credit Card'], 'card_name': ['null'], 'status_message': ['I wish to review my order again before completing the transaction.'],
         'currency': ['USD'], 'amount': ['750.0'], 'billing_name': ['Mitchell Admin'], 'billing_address': ['215 Vine St'], 
         'billing_city': ['Scranton'], 'billing_state': ['Pennsylvania'], 'billing_zip': ['18503'], 
         'billing_country': ['United States'], 'billing_tel': ['1 555-555-5555'], 'billing_email': ['admin@yourcompany.example.com'], 'vault': ['N'],
          'offer_type': ['null'], 'offer_code': ['null'], 'discount_value': ['0.0'], 'mer_amount': ['750.0'], 'bank_qsi_no': ['null'],
           'bank_receipt_no': ['null\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b']}
         """
        
        self.ensure_one()
        status = data.get('order_status', False)[0]
        print(status)
        TransactionTypeId = ""
        print(TransactionTypeId)
        if data.get('payment_mode', False):
            TransactionTypeId = data.get('payment_mode', False)[0]

        res = {
            'acquirer_reference': data.get('tracking_id')[0] ,
            'state_message':str(data.get('status_message')[0]),
            'CCAvenue_txn_type':TransactionTypeId
            # 'state_message': "Transaction ID : "+str(data.get("TransactionId", False))+", Bank :"+str(data.get("Bank_Name", False))+", Date :"+str(data.get("Date", False))
        }
        
        if (status == 'Success'):
            _logger.info('Validated CCAvenue payment for tx %s: set as done' % (self.reference))
            res.update(state='done', date=fields.Datetime.now())
            self._set_transaction_done()
            self.write(res)
            self.execute_callback()
            return True
        # elif data.get('AUTH_STATUS_NO', False) == '00':
        #     _logger.info('System Error, Received notification for CCAvenue payment %s: set as Error' % (self.reference))
        #     res.update(state='error')
        #     self._set_transaction_error()
        #     return self.write(res)
        # elif (data.get('AUTH_STATUS_NO', False) == '03'):
        #     _logger.info('Transaction declined by Issuer (Insufficient balance/transaction limit exceed).Received notification for CCAvenue payment %s: set as Cancel' % (self.reference))
        #     res.update(state='cancel')
        #     self._set_transaction_cancel()
        #     return self.write(res)
        # elif (data.get('AUTH_STATUS_NO', False) == '02'):
        #     _logger.info('Transaction cancelled by Customer. Received notification for CCAvenue payment %s: set as Cancel' % (self.reference))
        #     res.update(state='cancel')
        #     self._set_transaction_cancel()
        #     return self.write(res)
        else:
            error = 'Received cancelled status for CCAvenue payment %s: %s, set as Cancelled' % (self.reference, status)
            _logger.info(error)
            res.update(state='cancel', state_message=error)
            self._set_transaction_cancel()
            return self.write(res)
    
    
    
    
