from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from odoo.tools.misc import formatLang, get_lang

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        print(self.price_unit,'1111111111111111')
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv
        print(self.price_unit,'22222222222222222')
        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav
        print(self.price_unit,'33333333333333333')
        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0
        print(self.price_unit,'444444444444444444')
        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        print(self.price_unit,'555555555555555555')
        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))
        print(self.price_unit,'6666666666666666666')
        self._compute_tax_id()
        print('proooooooooooo')
        print(self.price_unit,'777777777777777777')
        if self.order_id.pricelist_id and self.order_id.partner_id and self.product_id.product_used == 'none':
            print('proooooooooooo22222222')
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        
        
        print(self.price_unit,'000000000000000000000')
        self.update(vals)
        print(self.price_unit,'000000000000000000000')

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s", product.name)
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False
        print(self.price_unit,'000000000000000000000')
        return result





