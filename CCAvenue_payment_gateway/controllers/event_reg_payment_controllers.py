# -*- coding: utf-8 -*-
###################################################################################
#
#
###################################################################################

import logging
import pprint
import werkzeug
from werkzeug.utils import redirect
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.payment.controllers.portal import PaymentProcessing
import requests
import json
from string import Template
from Crypto.Cipher import AES
from Crypto import Random
import re, hashlib

_logger = logging.getLogger(__name__)

class CCAvenueController(http.Controller):
    
    @http.route(['/event/registration/ccavenue/response','/event/registration/ccavenue/return', '/event/registration/ccavenue/cancel', '/event/registration/ccavenue/error'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def event_registration_CCAvenue_response(self,**post):
        # acquirer_id = request.env['payment.acquirer'].sudo().search([('provider','=','CCAvenue')], limit=1)
        
        # if acquirer_id:
        # post['acquirer_id'] = acquirer_id
        
        def decrypt(cipherText):
            iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
            decDigest = hashlib.md5()
            decDigest.update(str('8BE48647FC5943EA64085EE6DAE7DAE1').encode())
            encryptedText = bytes.fromhex(cipherText)
            dec_cipher = AES.new(decDigest.digest(), AES.MODE_CBC, iv)
            decryptedText = dec_cipher.decrypt(encryptedText).decode("utf-8")
            
            params = re.findall(r'([^=&]+)=([^=&]+)', decryptedText)
            res = dict()
            for key, val in params:
                res.setdefault(key, []).append(val)
                
            return res

        if post:
            post = decrypt(post.get('encResp',False))
            event_reg_id = request.env['event.registration'].sudo().search([('id','=',post['order_id'][0])], limit=1)
            render_ctx = {}
            if post['order_status'][0] == 'Success':
                # appointment_id.payment_status_apt = "paid"
                
                render_ctx.update({
                    'email': event_reg_id.partner_id.email or '',
                    'event_ref': event_reg_id.event_id.name or '',
                    'success': True or '',
                    'event_reg_id': event_reg_id.id,
                    'amount': post['amount'][0],
                    })
                return request.render("ppts_website_theme.website_event_reg_pos_payment_success_page", render_ctx)
            else:
                render_ctx.update({
                    'email': event_reg_id.partner_id.email or '',
                    'event_ref': event_reg_id.event_id.name or '',
                    'success': '',
                    'event_reg_id': event_reg_id.id,
                    'amount': post['amount'][0],
                    })
                # return werkzeug.utils.redirect('/appointment/ccavenue/success/'+str(appointment_id.id))
                return request.render("ppts_website_theme.website_event_reg_pos_payment_success_page", render_ctx)

    
    @http.route(['/event/registration/ccavenue/request/<string:apt>/<string:amount>'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def event_registration_CCAvenue_request(self, apt, amount,**post):
        print('---')
        accessCode = 'AVWB04JK42AU13BWUA' 	
        workingKey = '8BE48647FC5943EA64085EE6DAE7DAE1'
        
        def pad(data):
            length = 16 - (len(data) % 16)
            data += chr(length)*length
            return data

        def encrypt(plainText,workingKey):
            iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
            plainText = pad(plainText)
            encDigest = hashlib.md5()
            encDigest.update(workingKey.encode())
            enc_cipher = AES.new(encDigest.digest(), AES.MODE_CBC, iv)
            encryptedText = enc_cipher.encrypt(plainText.encode('utf-8')).hex()
            return encryptedText

        event_reg_id = request.env['event.registration'].sudo().browse(int(apt))
        print(event_reg_id,':::::::::::::::::::;')
        if event_reg_id.event_payment_status == "paid":
            render_ctx = {}
            render_ctx.update({
               'email': event_reg_id.partner_id.email or '',
                'event_ref': event_reg_id.event_id.name or '',
                'success': True or '',
                'event_reg_id': event_reg_id.id,
                'amount': post['amount'][0],
                'paid_already' : True,
                })
            return request.render("ppts_website_theme.website_event_reg_pos_payment_success_page", render_ctx)

        p_merchant_id = '45990'
        p_order_id = str(event_reg_id.id) #order_id
        p_currency = 'AED'
        p_amount = amount #amount
        p_redirect_url = 'https://illuminations.pptssolutions.com/event/registration/ccavenue/response' #redirect_url
        p_cancel_url = 'https://illuminations.pptssolutions.com/event/registration/ccavenue/cancel' #cancel_url
        p_language = 'EN' #language
        p_billing_name = event_reg_id.sales_person.partner_id.name or ''#billing_name
        p_billing_address = event_reg_id.sales_person.partner_id.street or '' #billing_address
        p_billing_city = event_reg_id.sales_person.partner_id.city_id.name or '' #billing_city
        p_billing_state = event_reg_id.sales_person.partner_id.state_id.name or '' #billing_state
        p_billing_zip = event_reg_id.sales_person.partner_id.zip or '' #billing_zip
        p_billing_country = event_reg_id.sales_person.partner_id.country_id.name or '' #billing_country
        p_billing_tel = event_reg_id.sales_person.partner_id.mobile or '' #billing_tel
        p_billing_email = event_reg_id.sales_person.partner_id.email or '' #billing_email

        p_delivery_name = event_reg_id.partner_id.name or '' #delivery_name
        p_delivery_address = event_reg_id.partner_id.street or '' #delivery_address
        p_delivery_city =  event_reg_id.partner_id.city_id.name or '' #delivery_city
        p_delivery_state = event_reg_id.partner_id.state_id.name or '' #delivery_state
        p_delivery_zip = event_reg_id.partner_id.zip or '' #delivery_zip
        p_delivery_country = event_reg_id.partner_id.country_id.name or '' #delivery_country
        p_delivery_tel = event_reg_id.partner_id.mobile or '' #delivery_tel
        p_merchant_param1 = 'additional Info.' #merchant_param1
        p_merchant_param2 = 'additional Info.' #merchant_param2
        p_merchant_param3 = 'additional Info.' #merchant_param3
        p_merchant_param4 = 'additional Info.' #merchant_param4
        p_merchant_param5 = 'additional Info.' #merchant_param5
        p_integration_type = 'iframe_normal' #integration_type
        p_promo_code = '' #promo_code
        p_customer_identifier = str(event_reg_id.partner_id.id) or ''
        print(p_customer_identifier,'llllllllllllllllllll') #Customer Id

        merchant_data = 'merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'integration_type='+p_integration_type+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
        print(merchant_data,'>>>>>>>>>>>>>>>>>>>>>>>>>>')
        encryption = encrypt(merchant_data,workingKey)

        html = '''\
            <html>
            <head>
                <title>Sub-merchant checkout page</title>
                <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
            </head>
            <body>
                <center>
                <!-- width required mininmum 482px -->
                    <iframe  width="482" height="500" scrolling="No" frameborder="0"  id="paymentFrame" src="https://secure.ccavenue.ae/transaction/transaction.do?command=initiateTransaction&merchant_id=$mid&encRequest=$encReq&access_code=$xscode">
                    </iframe>
                </center>
                
                <script type="text/javascript">
                    $(document).ready(function(){
                        $('iframe#paymentFrame').load(function() {
                            window.addEventListener('message', function(e) {
                                $("#paymentFrame").css("height",e.data['newHeight']+'px'); 	 
                            }, false);
                        }); 
                    });
                </script>
            </body>
            </html>
        '''
        return Template(html).safe_substitute(mid=p_merchant_id,encReq=encryption,xscode=accessCode)
    
    
    
    #Website payment
 