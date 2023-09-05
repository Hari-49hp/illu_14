


import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random

merchant_id = '47662'
workingKey = '114AECA15989D55CA45B279DAA9F9568'
accessCode = 'AVTZ03HL62AL72ZTLA'



def pad(data):
    length = 16 - (len(data) % 16)
    data += chr(length)*length
    return data

def encrypt(plainText,workingKey):
    iv = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plainText = pad(plainText)
    workingKey =  hashlib.md5(workingKey.encode("utf-8")).digest()
    cipher = AES.new(workingKey, AES.MODE_CBC, iv)
    encryptedText = cipher.encrypt(plainText.encode("utf-8")).hex()
    print(encryptedText)
    return encryptedText



def create_ccavenu_payment():
    p_merchant_id = merchant_id
    p_order_id = 'S066'
    p_currency = 'INR'
    p_amount = '100'
    p_redirect_url = 'https://illuminations.ae'
    p_cancel_url = 'https://illuminations.ae'
    p_language = 'EN'
    p_billing_name = 'jana'
    p_billing_address='test'
    p_billing_city='test'
    p_billing_state = 'test'
    p_billing_zip = '559'
    p_billing_country = 'India'
    p_billing_tel = '7897978687'
    p_delivery_name = 'jana'
    p_delivery_address='test'
    p_delivery_city='test'
    p_delivery_state = 'test'
    p_delivery_zip = '559'
    p_delivery_country = 'India'
    p_delivery_tel = '7897978687'
    p_merchant_param1 = ''
    p_merchant_param2 = ''
    p_merchant_param3 = ''
    p_merchant_param4 = ''
    p_merchant_param5 = ''
    p_promo_code = ''
    p_billing_email = 'test@gmail.com'
    
    
    
    merchant_data='merchant_id='+p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+\
                'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+\
                'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+\
                'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+\
                'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+\
                'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+\
                'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+\
                'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+\
                'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'
    
    encrypttext = encrypt(merchant_data, workingKey)
    
    

encrptext = create_ccavenu_payment()
print(encrptext)
    
    
    




