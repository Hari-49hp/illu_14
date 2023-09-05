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
    
    @http.route(['/appointment/ccavenue/response','/appointment/ccavenue/return', '/appointment/ccavenue/cancel', '/appointment/ccavenue/error'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def appointment_CCAvenue_response(self,**post):
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
            appointment_id = request.env['appointment.appointment'].sudo().search([('sequence','=',post['order_id'][0])], limit=1)
            render_ctx = {}
            if post['order_status'][0] == 'Success':
                # appointment_id.payment_status_apt = "paid"
                
                render_ctx.update({
                    'email': appointment_id.partner_id.email or '',
                    'appoinment_ref': appointment_id.sequence or '',
                    'success': True or '',
                    'appoinment_id': appointment_id.id,
                    'amount': post['amount'][0],
                    })
                return request.render("ppts_website_theme.website_appointment_pos_payment_success_page", render_ctx)
            else:
                render_ctx.update({
                    'email': appointment_id.partner_id.email or '',
                    'appoinment_ref': appointment_id.sequence or '',
                    'success': '',
                    'appoinment_id': appointment_id.id,
                    'amount': post['amount'][0],
                    })
                # return werkzeug.utils.redirect('/appointment/ccavenue/success/'+str(appointment_id.id))
                return request.render("ppts_website_theme.website_appointment_pos_payment_success_page", render_ctx)

    
    @http.route(['/appointment/ccavenue/request/<string:apt>/<string:amount>'], methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def appointment_CCAvenue_request(self, apt, amount,**post):
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

        appointment_id = request.env['appointment.appointment'].sudo().browse(int(apt))
        
        if appointment_id.payment_status_apt == "paid":
            render_ctx = {}
            render_ctx.update({
                'email': appointment_id.partner_id.email or '',
                'appoinment_ref': appointment_id.sequence or '',
                'success': True or '',
                'appoinment_id': appointment_id.id,
                'amount': 0,
                'paid_already' : True,
                })
            return request.render("ppts_website_theme.website_appointment_pos_payment_success_page", render_ctx)
            

        p_merchant_id = '45990'
        p_order_id = appointment_id.sequence #order_id
        p_currency = 'AED'
        p_amount = amount #amount
        p_redirect_url = 'https://illuminations.pptssolutions.com/appointment/ccavenue/response' #redirect_url
        p_cancel_url = 'https://illuminations.pptssolutions.com/appointment/ccavenue/cancel' #cancel_url
        p_language = 'EN' #language
        p_billing_name = appointment_id.sales_rep_id.partner_id.name or ''#billing_name
        p_billing_address = appointment_id.sales_rep_id.partner_id.street or '' #billing_address
        p_billing_city = appointment_id.sales_rep_id.partner_id.city_id.name or '' #billing_city
        p_billing_state = appointment_id.sales_rep_id.partner_id.state_id.name or '' #billing_state
        p_billing_zip = appointment_id.sales_rep_id.partner_id.zip or '' #billing_zip
        p_billing_country = appointment_id.sales_rep_id.partner_id.country_id.name or '' #billing_country
        p_billing_tel = appointment_id.sales_rep_id.partner_id.mobile or '' #billing_tel
        p_billing_email = appointment_id.sales_rep_id.partner_id.email or '' #billing_email

        p_delivery_name = appointment_id.partner_id.name or '' #delivery_name
        p_delivery_address = appointment_id.partner_id.street or '' #delivery_address
        p_delivery_city =  appointment_id.partner_id.city_id.name or '' #delivery_city
        p_delivery_state = appointment_id.partner_id.state_id.name or '' #delivery_state
        p_delivery_zip = appointment_id.partner_id.zip or '' #delivery_zip
        p_delivery_country = appointment_id.partner_id.country_id.name or '' #delivery_country
        p_delivery_tel = appointment_id.partner_id.mobile or '' #delivery_tel
        p_merchant_param1 = 'additional Info.' #merchant_param1
        p_merchant_param2 = 'additional Info.' #merchant_param2
        p_merchant_param3 = 'additional Info.' #merchant_param3
        p_merchant_param4 = 'additional Info.' #merchant_param4
        p_merchant_param5 = 'additional Info.' #merchant_param5
        p_integration_type = 'iframe_normal' #integration_type
        p_promo_code = '' #promo_code
        p_customer_identifier = str(appointment_id.partner_id.id) or '' #Customer Id

        merchant_data = 'merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'integration_type='+p_integration_type+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
	
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
    @http.route(['/payment/CCAvenue/response','/payment/CCAvenue/return', '/payment/CCAvenue/cancel', '/payment/CCAvenue/error'],
                methods=['GET', 'POST'], type='http', auth='public', csrf=False)
    def CCAvenue_return(self, **post):
        """CCAvenue."""
        
        acquirer_id = request.env['payment.acquirer'].sudo().search([('provider','=','CCAvenue')], limit=1)
        
        if acquirer_id:
            post['acquirer_id'] = acquirer_id
        
        print(post)
        
        if post:
            post = acquirer_id.decrypt(post.get('encResp',False))
            post.popitem()
            print('_________________________________')
            print(post)
            request.env['payment.transaction'].sudo().form_feedback(post, 'CCAvenue')
        _logger.info(
            'CCAvenue: Response Post Data %s', pprint.pformat(post))
        _logger.info(str(post))
        
        reference = post.get('order_id', [])[0]
        
        if not request.session.get("__payment_tx_ids__", []) and reference:
            txt_id = request.env['payment.transaction'].sudo().search([('reference','=',reference)], limit=1)
            tx_ids_list = set(request.session.get("__payment_tx_ids__", [])) | set(txt_id.ids)
            request.session["__payment_tx_ids__"] = list(tx_ids_list)
        
        
        return werkzeug.utils.redirect('/payment/process')
    
    @http.route(['/partner_card/filter'], type='http', auth="public", website=True, csrf=False, cros='*')
    def website_partner_card_filter(self, **post):
        domain = [];cards = []
        if 'partner_invoice_id' in post and post['partner_invoice_id'] != '':
            domain.append(('partner_id','=',int(post['partner_invoice_id'])))
        elif not ('CCAvenue_partner_card_id' in post and post['CCAvenue_partner_card_id'] != ''):
            domain.append(('id','=',0))
            
        
        if 'CCAvenue_partner_card_id' in post and post['CCAvenue_partner_card_id'] != '':
            domain.append(('id','=',int(post['CCAvenue_partner_card_id'])))
        
        card_ids = request.env['payment.token'].sudo().search((domain))
        for card_id in card_ids:
            cards.append({
                    "id":card_id.id,
                    'name':str(card_id.cc_avenue_name or '')+'-'+str(card_id.cc_avenue_number or ''),
                    'cc_avenue_number':card_id.cc_avenue_number or '',
                    'cc_avenue_cvc':card_id.cc_avenue_cvc or '',
                    'cc_avenue_name':card_id.cc_avenue_name or '',
                    'cc_avenue_expiry':card_id.cc_avenue_expiry or '',
                })
            
        print(cards)
        return json.dumps(cards)
    
    
class WebsiteSale(WebsiteSale):
    
    @http.route(['/shop/payment/transaction/',
        '/shop/payment/transaction/<int:so_id>',
        '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        if kwargs.get("CCAvenue_bank_id", False):
            request.session['CCAvenue_bank_id'] = kwargs.get("CCAvenue_bank_id", False)
            request.session['cc_number'] = kwargs.get("cc_number", False)
            request.session['cc_cvc'] = kwargs.get("cc_cvc", False)
            request.session['cc_expiry'] = kwargs.get("cc_expiry", False)
            request.session['cc_holder_name'] = kwargs.get("cc_holder_name", False)
            request.session['ccavenue_save_token'] = kwargs.get("ccavenue_save_token", False)
            request.session['cc_brand'] = kwargs.get("cc_brand", False)
        response = super(WebsiteSale, self).payment_transaction(acquirer_id, save_token, so_id, access_token, token)
        return response
    
    
class PaymentProcessing(PaymentProcessing):
    
    @http.route(['/payment/process'], type="http", auth="public", website=True, sitemap=False)
    def payment_status_page(self, **kwargs):
        
        
        response = super(PaymentProcessing, self).payment_status_page()
        # When the customer is redirect to this website page,
        # we retrieve the payment transaction list from his session
        tx_ids_list = self.get_payment_transaction_ids()
        payment_transaction_ids = request.env['payment.transaction'].sudo().browse(tx_ids_list).exists()

        render_ctx = {
            'payment_tx_ids': payment_transaction_ids.ids,
            'email':'',
            'appoinment_ref':'',
            'success':False,
            'appoinment_id':False,
        }
        
        order = request.website.sale_get_order()
        
        event = False
        
        if payment_transaction_ids:
        
            for payment_transaction_id in payment_transaction_ids:
                appoinment_ref = ""
                appoinment_id = False
                appoinment_obj_id = False
                success = False
                for sale_order_id in payment_transaction_id.sale_order_ids:
                    appoinment_id = request.env['appointment.appointment'].sudo().search([('sale_order_id','=',sale_order_id.id)])
                    if appoinment_id:
                        appoinment_ref = appoinment_id.sequence
                        appoinment_obj_id = appoinment_id
                        appoinment_id = appoinment_id.id
                        
                        if payment_transaction_id.state == 'done':
                            appoinment_obj_id.website_payment_status = "paid"
                            success = True
                        else:
                            appoinment_obj_id.website_payment_status = "no_paid"
                        appoinment_obj_id._compute_payment_from_payment()
                        if not sale_order_id.invoice_count and  appoinment_obj_id.payment_status_apt == 'no_paid':
                            sale_order_id.create_invoice_website()
                        if not sale_order_id.invoice_count and  appoinment_obj_id.payment_status_apt == 'paid':
                            sale_order_id.create_invoice_website_paid()
                
                        render_ctx.update({
                            'email':payment_transaction_id.partner_id.email or '',
                            'appoinment_ref':appoinment_ref or '',
                            'success':success or '',
                            'appoinment_id':appoinment_id,
                            })
                        event = False
                        # return request.render("ppts_website_theme.website_appointment_payment_success_page", render_ctx)
                    
                    else:
                        event = True
                        event_reg_id = request.env['event.registration'].sudo().search([('sale_order_id','=',sale_order_id.id)])
                        
                        
                        if payment_transaction_id.state == 'done':
                            event_reg_id.write({"website_payment_status": "paid"})
                            success = True
                        else:
                            event_reg_id.write({"website_payment_status": "no_paid"})
                            
                        
                        
                        for event_reg in event_reg_id:
                            event_reg._compute_payment_from_payment()
                            # if not sale_order_id.invoice_count:
                            #     sale_order_id.create_invoice_website()
                            if not sale_order_id.invoice_count and  event_reg_id.website_payment_status == 'no_paid':
                                sale_order_id.create_invoice_website()
                            if not sale_order_id.invoice_count and  event_reg_id.website_payment_status == 'paid':
                                sale_order_id.create_invoice_website_paid()
                        render_ctx = {
                            'email':sale_order_id.partner_id.email or '',
                            'event_ref':event_reg_id[0].event_id.name or '',
                            'success':success,
                            'event_id':event_reg_id[0].event_id.id,
                            'sale_id':sale_order_id.id,
                        }
                        # return request.render("ppts_website_theme.website_event_payment_success_page", render_ctx)
                        
        elif order:
            appoinment_ref = ""
            appoinment_id = False
            success = True
            for sale_order_id in order:
                appoinment_id = request.env['appointment.appointment'].sudo().search([('sale_order_id','=',sale_order_id.id)])
                if appoinment_id:
                    appoinment_ref = appoinment_id.sequence
                    appoinment_id = appoinment_id.id
                        
                    render_ctx.update({
                        'email':sale_order_id.partner_id.email or '',
                        'appoinment_ref':appoinment_ref or '',
                        'success':success or '',
                        'appoinment_id':appoinment_id,
                        })
                    event = False
                    # return request.render("ppts_website_theme.website_appointment_payment_success_page", render_ctx)
                else:
                    event = True
                    event_reg_id = request.env['event.registration'].sudo().search([('sale_order_id','=',sale_order_id.id)],limit=1)
                        
                    render_ctx = {
                        'email':sale_order_id.partner_id.email or '',
                        'event_ref':event_reg_id.event_id.name or '',
                        'success':success or '',
                        'event_id':event_reg_id.event_id.id,
                        'sale_id':sale_order_id.id,
                    }
                    # return request.render("ppts_website_theme.website_event_payment_success_page", render_ctx)
        if event:
            return request.render("ppts_website_theme.website_event_payment_success_page", render_ctx)
        else:
            return request.render("ppts_website_theme.website_appointment_payment_success_page", render_ctx)
                    
    
    
    
    
