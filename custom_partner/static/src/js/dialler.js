// load the xml files using ajax 07-09-22
odoo.define('custom_partner.voip_dialler', function (require) {

'use strict';

var core = require('web.core');

var ajax = require('web.ajax');
// call the customized mail template 
var qweb = core.qweb;
ajax.loadXML('/custom_partner/static/src/xml/phone_call_dialler.xml', qweb);
});