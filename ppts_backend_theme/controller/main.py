# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
import json
from datetime import datetime

class WebMenusList(http.Controller):
    @http.route(['/web/custom/details'], type='http', auth="public", website=True, csrf=False)
    def web_menus(self, **post):
        menus_ids = request.env['ir.ui.menu'].search([('parent_id','=',False)])
        vals = {};lst_name = [];
        for i in menus_ids:
        	img = i.web_icon
        	x_img = img.replace(",", "/")
        	lst_name.append(i.name+"$$$$"+"/web#menu_id="+str(i.id)+"&action_id=0"+"$$$$"+str(x_img))
        vals['name'] = lst_name
        return json.dumps(vals) 