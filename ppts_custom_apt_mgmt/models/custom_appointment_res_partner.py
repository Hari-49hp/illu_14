from odoo import api, fields, models, _
import re
from odoo.exceptions import UserError, ValidationError

class ResCountry(models.Model):
    _inherit = 'res.country'

    mobile_number_limit = fields.Integer('Mobile Number Limit')

class CustompartnerApt(models.Model):
    _inherit = ['res.partner']

    mobile_num =fields.Char('Full Mobile',compute='_compute_contact_mobile',store=True)
    phone_num =fields.Char('Full Phone',compute='_compute_contact_mobile',store=True)

    def get_company_address(self):
        address = ''
        address += self.street+',' if self.street else ''
        address += self.street2+',' if self.street2 else ''
        address += self.city+',' if self.city else ''
        address += self.state_id.name+',' if self.state_id else ''
        address += self.zip+',' if self.zip else ''
        address += self.country_id.name+',' if self.country_id else ''
        return address
        
    def _compute_get_company_address(self):
        for rec in self:
            rec.single_line_address = ''
            rec.single_line_address = rec.get_company_address()

    single_line_address = fields.Char('Address', compute="_compute_get_company_address")
    
    @api.onchange('mobile')
    def _onchange_mobileChangesStrip(self):
        def RepresentsInt(s):
            try: 
                int(s)
                return True
            except ValueError:
                return False
        
        if self.mobile:
            change = "".join(self.mobile.split())
            if RepresentsInt(change) == False:
                change = re.sub('[^0-9]','', change)
                self.mobile = change
                return {
                        'warning': {
                        'title': _('Warning'),
                        'message': _('Mobile should not be character')}
                        }
            else: self.mobile = change

    @api.depends('mobile','phone','street','email')
    def _compute_contact_mobile(self):
        for partner in self:
            if partner.mobile:
                partner.mobile_num = (re.sub(r'\s+', '', str(partner.mobile)).strip())
            else:
                partner.mobile_num = False
            if partner.phone:
                partner.phone_num = (re.sub(r'\s+', '', str(partner.phone)).strip())
            else:
                partner.phone_num = False

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []

        if name:
            domain = ['|', '|', '|','|', '|', ('name', operator, name), \
                ('phone', operator, name),('phone_num', operator, name), ('email', operator, name),
                      ('mobile', operator, name), ('mobile_num', operator, name)]
        return self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)

# class Partner(models.Model):
#     _name = 'res.partner'
#     _inherit = ['res.partner', 'phone.validation.mixin']

#     @api.onchange('phone', 'country_id', 'company_id')
#     def _onchange_phone_validation(self):
#         if self.phone:
#             self.phone = self.phone #self.phone_format()

#     @api.onchange('mobile', 'country_id', 'company_id')
#     def _onchange_mobile_validation(self):
#         if self.mobile:
#             if not self.country_id.mobile_number_limit == 0:
#                 if len(self.mobile) != self.country_id.mobile_number_limit:
#                     raise UserError(_("Mobile number %s digits atleast !!" % (self.country_id.mobile_number_limit)))
#             self.mobile = self.mobile