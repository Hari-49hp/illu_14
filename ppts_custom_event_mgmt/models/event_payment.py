from datetime import date, datetime, timedelta, time
from email.policy import default
from itertools import product

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
import datetime
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
import pytz
from odoo.tools.misc import formatLang

class EventRegistrationConfirmation(models.Model):
    _name = "event.registration.confirmation"
    _rec_name = "event_id"
    _description = 'Event Registration Confirmation'

    @api.depends('lines')
    def _compute_price_total(self):
        for order in self:
            currency = order.currency_id
            order.amount_tax = currency.round(sum(self._amount_line_tax(line) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal_incl for line in order.lines))
            amount_sub_untaxed = currency.round(sum(line.price_unit*line.qty for line in order.lines))
            
            order.amount_discount = -1 * currency.round(sum(line.amount_discount for line in order.lines))
            order.amount_sub_total = amount_sub_untaxed
            order.amount_total = amount_untaxed

    @api.depends('lines')
    def _compute_line_description(self):
        for rec in self:
            rec.write({
                'line_description': rec.lines.ids
            })


    event_id = fields.Many2one('event.registration', string='Event')
    partner_id = fields.Many2one('res.partner', string='Name')
    user_id = fields.Many2one('res.users',string="User",default=lambda self: self.env.user)

    cheque = fields.Char('Cheque #')
    payment_method_id = fields.Many2many('pos.payment.method', string='Payment Method')

    customer_code = fields.Char(string='Customer Code', related='partner_id.sequence')
    mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    email = fields.Char(string='Email', related='partner_id.email')

    # sequence = fields.Char(related='event_id.sequence')
    sequence = fields.Char(compute="_compute_event_ref")
    address_single_line = fields.Char(string="Address")
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    zip = fields.Char(related='partner_id.zip')
    city_id = fields.Many2one('city.master',string='City', related='partner_id.city_id')
    state_id = fields.Many2one("res.country.state", string='State', related='partner_id.state_id')
    country_id = fields.Many2one('res.country', string='Country', related='partner_id.country_id')
    company_id = fields.Many2one('res.company', string='Venue', change_default=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    gender = fields.Selection(string="Gender", related='partner_id.gender')
    location_ids = fields.Many2many('res.company',string='Locations',compute="get_location_ids")
    # booking_ref = fields.Char('Booking Ref. #', related='appointments_id.sequence')
    sales_rep_id = fields.Many2one('res.users',string='Sales Rep.')
    # sales_rep_id = fields.Many2one('res.users',string='Sales Rep.', related='event_id.sales_person')
    lines = fields.One2many('event.retail.product', 'event_confirmation_id', string='Order Details')
    line_description = fields.Many2many('event.retail.product', 'line_description_new_order_table',\
        string="Order Summary", compute="_compute_line_description")
    amount_tax = fields.Float(string='Taxes', digits=0, compute='_compute_price_total')
    amount_sub_total = fields.Float(string='Sub Total', digits=0, compute='_compute_price_total')
    amount_total = fields.Float(string='Total', digits=0, compute='_compute_price_total')
    amount_discount = fields.Float(string='Discount', digits=0, compute='_compute_price_total')
    product_categ_id = fields.Many2one('product.category', string='Show')
    product_id = fields.Many2one('product.product', string='Search By')
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)
    discount = fields.Float(string='Discount', digits=0, default=0.0)
    discount_type = fields.Selection([('flate_rate','Flate Rate'),('percentage','Percentage')], default='percentage', string='Discount Type', required=True)

    partner_credit = fields.Float('Credit Balance', related="partner_id.customer_balance")
    credit_reconcile = fields.Float('Enter the amount')
    single_prod_subtotal = fields.Float(string="Subtotal",compute="_compute_cal_prod_subtotal")

    @api.depends('partner_id')
    def get_location_ids(self):
        self.location_ids = self.event_id.company_id.ids

    # get the event sequence with customer name for sequence fields
    # pass the sales person
    @api.depends('partner_id')
    def _compute_event_ref(self):
        
        self.sequence = self.event_id.event_id.event_seq + '/'+ self.event_id.partner_id.name
        self.sales_rep_id = self.event_id.sales_person.id
        self.address_single_line = self.partner_id.single_line_address
        self.partner_id = self.event_id.partner_id.id


    # pass the product price while select the product 01-07-22
    @api.onchange('product_id')
    def product_price(self):
        self.price_unit = self.product_id.list_price


    # calculate the subtotal for single product 21-09-22
    @api.depends('qty','price_unit','discount','discount_type')
    def _compute_cal_prod_subtotal(self):
        self.single_prod_subtotal = self.qty * self.price_unit
        if self.discount and self.discount_type == 'percentage':
            sub_total = (self.qty * self.price_unit)
            self.single_prod_subtotal =sub_total - (sub_total * self.discount/100)
        else:
            sub_total = self.qty * self.price_unit
            self.single_prod_subtotal =sub_total - self.discount


    @api.depends('shipping_handling_overall', 'lines')
    def _compute_subtotal_overall(self):
        for rec in self:
            rec.subtotal_overall = 0
            rec.taxes_overall = 0
            rec.total_overall = 0
            total_values = 0.0
            for i in rec.lines:
                rec.subtotal_overall += i.total_amt
                rec.taxes_overall += i.price_subtotal_incl - i.price_subtotal
            total_values = rec.subtotal_overall + rec.amount_discount
            rec.total_overall = total_values + rec.taxes_overall + rec.shipping_handling_overall
            base_url = self.env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
            rec.quick_invoice_sms = 'Please pay your %s invoice bill of %s AED %s/event/registration/ccavenue/request/%s/%s' % (rec.event_id.name, str(rec.total_overall) ,base_url, str(rec.event_id.id), str(rec.total_overall))
            rec.payment_link = '%s/event/registration/ccavenue/request/%s/%s' % (base_url, str(rec.event_id.id), str(rec.total_overall))

    # subtotal_overall = fields.Float(string="Subtotal")
    subtotal_overall = fields.Float(string="Subtotal", compute="_compute_subtotal_overall")
    shipping_handling_overall = fields.Float(string="Shipping Handling", compute="_compute_subtotal_overall", readonly=False, store=True)
    taxes_overall = fields.Float(string="Taxes", compute="_compute_subtotal_overall")
    total_overall = fields.Float(string="Total", compute="_compute_subtotal_overall")

    customer_phone_number = fields.Char(string="Customer Phone Number", related='partner_id.mobile', readonly=False)
    quick_invoice_sms = fields.Text(string="Quick Invoice SMS")
    select_payment_mode = fields.Selection([('none','None'),('credit','Available Credit'),('online_payment','Online Payment')], default='none', string='Select Payment Mode')
    payment_link = fields.Text(string="Payment Link")

    def product_tax(self, product_id, amount):
        if product_id:
            total_included = 0
            for tax in product_id.taxes_id:
                taxes = tax.compute_all(amount, self.env.company.currency_id, 1, product=product_id.id, partner=False)
                t2 = taxes['total_included'] - amount
                total_included += t2
            return total_included

    # pass the order into an pos
    def apply_credit(self):

        if self.partner_credit < 0:
            raise UserError(_("Cannot apply amount when credit Balance is Negative ! "))

        if self.partner_credit < self.credit_reconcile:
            raise UserError(_("An amount greater than the credit balance cannot be applied ! "))
        if self.total_overall < self.credit_reconcile:
            raise UserError(_("An amount greater than the order total cannot be applied ! "))
        pos_lines = payment_lines = []
        pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
        if not pos_session_id:
            raise UserError(_("Please create a POS session to create POS order and confirm the Event Registration"))

        seq = self.env['ir.sequence'].search([('name','=','POS EVT'),('code','=','POS EVT')])
        if seq:
            pos_seq = seq.next_by_id()
        else:
            seq =  self.env['ir.sequence'].create({'name': 'POS EVT','code':'POS EVT','active':True,'implementation':'no_gap','prefix':'EVT/APT','padding':5,'number_increment':1,'number_next_actual':1})
            pos_seq = seq.next_by_id()

        pos_lines = []
        for rec in self.lines:
            l_id = self.env['event.retail.product'].browse(rec.id)
            vals = ([0, 0, {
                'full_product_name': l_id.product_id.name,
                'product_id': l_id.product_id.id,
                'qty': rec.qty,
                'price_subtotal': l_id.price_subtotal,
                'price_subtotal_incl':l_id.price_subtotal_incl,
                'order_id': rec.event_confirmation_id.event_id.pos_order_id.id,
                'discount': l_id.discount if l_id.discount_type == 'percentage' else 0.0,
                # 'absolute_discount': l_id.discount or 0.0,
                'tax_ids': l_id.tax_ids.ids,
                'tax_ids_after_fiscal_position': l_id.tax_ids.ids,
                'price_unit': l_id.price_unit,
                'name': l_id.product_id.name,
            }])
            pos_lines.append(vals)
        payment_method_id = self.env['pos.payment.method'].search([('credit_jr','=', True)], limit=1)
        # payment_lines.append([0, 0, {
        #     'payment_method_id': payment_method_id.id,
        #     'amount': self.credit_reconcile,
        # }])

        
        sale_id = self.env['pos.order'].sudo().create({
                'partner_id': self.partner_id.id,
                'pricelist_id': 1,
                'session_id': pos_session_id.id,
                'amount_tax': 0.0,
                'amount_paid': 0.0,
                'amount_return': 0.0,
                'amount_total': 0.0,
                'state': 'draft',
                'sale_type_for': 'event',
                'company_id': self.event_id.company_id.id,
                'name': self.sequence,
                'pos_reference': pos_seq,
                'event_reg_id':self.event_id.id,
                'lines':pos_lines
                })

        self.event_id.pos_order_id = sale_id.id
        self.event_id.pos_order_id._onchange_amount_all()

        self.env['pos.payment'].create({
            'payment_method_id': payment_method_id.id,
            'amount': self.credit_reconcile,
            'pos_order_id': sale_id.id,
        })

        if self.credit_reconcile >= self.total_overall:
            sale_id.state = 'paid'

       

    def preview_invoice(self):
        print('090909090909090909')

    def send_by_sms(self):
        print('090909090909090909')
        # get_whatsapp_template = self.env['']
        # if self.partner_id.mobile and note_id.apt_cancel_whatsapp:
        #     rec.whatsapp_sent(partner_id=rec.partner_id.id,tmpl_id=note_id.apt_cancel_whatsapp.id,pt='res_partner',apt=self.id)

    def add_item(self):
        if not self.product_id:
            raise UserError(_("Please select product to continue !!"))
        
        if self.qty < 1:
            raise UserError(_("Quantity should not be less then 1 !!"))

        self.env['event.retail.product'].create({
                'product_id': self.product_id.id,
                'qty': self.qty,
                'price_subtotal': self.price_unit,
                'price_subtotal_incl': self.price_unit + self.product_tax(self.product_id, self.price_unit),
                'discount': self.discount,
                'discount_type': self.discount_type,
                'price_unit': self.price_unit,
                'name': self.product_id.name,
                'event_confirmation_id': self.id,
        })


        self.product_categ_id = self.qty = 1
        self.product_id = False
        self.price_unit = self.discount = 0.0
        self.discount_type = 'percentage'

        return {
                'type': 'ir.actions.act_window',
                'name': _('Pay Now'),
                'res_model': 'event.registration.confirmation',
                'res_id': self.id,
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
            }

    def proforma_invoice(self):
        return self.env.ref('ppts_custom_event_mgmt.action_event_reg_proforma_invoice').report_action(self)

    # using to send the mail with attachment
    def send_email(self):
        template_id = self.env.ref('ppts_custom_event_mgmt.event_proforma_email_template')
        template = self.env['mail.template'].search([('model', '=', 'mail.compose.message')], limit=1)
        ctx = dict(
            default_model='event.registration.confirmation',
            default_res_id=self.id,
            default_res_model='event.registration.confirmation',
            default_use_template=bool(template_id),
            default_template_id=template_id and template_id.id or False,
            default_composition_mode='comment',
            # custom_layout="mail.mail_notification_paynow",
            force_email=True
        )
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }



    
    def move_to_pos(self):

        line_vals = []
        for rec in self.lines:
            pos_session_id = self.env['pos.session'].search([('state', '=', 'opened')], limit=1)
            if not pos_session_id:
                raise UserError(_("Please create a POS session to create POS order and confirm the Appointment"))
            seq = self.env['ir.sequence'].search([('name','=','POS EVT'),('code','=','POS EVT')])
            if seq:
                pos_seq = seq.next_by_id()
            else:
                seq =  self.env['ir.sequence'].create({'name': 'POS EVT','code':'POS EVT','active':True,'implementation':'no_gap','prefix':'EVT/APT','padding':5,'number_increment':1,'number_next_actual':1})
                pos_seq = seq.next_by_id()

            vals = ([0, 0, {
                'full_product_name': rec.product_id.name,
                'product_id': rec.product_id.id,
                'qty': rec.qty,
                'price_subtotal': rec.price_subtotal,
                'price_subtotal_incl':rec.price_subtotal_incl,
                'order_id': rec.event_confirmation_id.event_id.pos_order_id.id,
                'discount': rec.discount if self.discount_type == 'percentage' else 0.0,
                # 'absolute_discount': rec.discount or 0.0,
                'tax_ids': rec.tax_ids.ids,
                'tax_ids_after_fiscal_position': rec.tax_ids.ids,
                'price_unit': rec.price_unit,
                'name': rec.product_id.name,
            }])
            line_vals.append(vals)
        get_prod = self.env['product.product'].search([('shipping_handling_charge','=',True)],limit=1)
        if self.shipping_handling_overall > 0 and get_prod:                
                values = ([0, 0, {
                'full_product_name': get_prod.name,
                'product_id': get_prod.id,
                'qty': 1,
                'price_subtotal': self.shipping_handling_overall,
                'price_subtotal_incl':self.shipping_handling_overall,
                'order_id': rec.event_confirmation_id.event_id.pos_order_id.id,
                'discount': 0.00,
                'absolute_discount': 0.00,
                'amount_discount':0.00,
                'tax_ids_after_fiscal_position': False,
                'price_unit': self.shipping_handling_overall,
                'name': get_prod.name,
                }])

                line_vals.append(values)
        if pos_session_id:
            pos_id = self.env['pos.order'].sudo().create({
                'partner_id': self.partner_id.id,
                'pricelist_id': 1,
                'session_id': pos_session_id.id,
                'amount_tax': 0.0,
                'amount_paid': 0.0,
                'amount_return': 0.0,
                'amount_total': 0.0,
                'state': 'draft',
                'sale_type_for': 'event',
                'company_id': self.event_id.company_id.id,
                'name': pos_seq,
                'pos_reference': pos_seq,
                'event_reg_id':self.event_id.id,
                'lines':line_vals
            })
            rec.event_confirmation_id.event_id.pos_order_id = pos_id.id
        if not rec.product_id.available_in_pos:
            rec.product_id.available_in_pos = True

        rec.event_confirmation_id.event_id.pos_order_id._onchange_amount_all()
        rec.event_confirmation_id.event_id.state='open'


    def _amount_line_tax(self, line):
        if line.product_id:
            total_included = price = 0
            if line.discount_type == 'percentage':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            else:
                price = line.price_unit - line.discount

            for tax in line.tax_ids:
                taxes = tax.compute_all(price, self.currency_id, line.qty, product=line.product_id, partner=False)
                t2 = taxes['taxes'][0]['amount']
                total_included += t2
            return total_included

    @api.onchange('lines')
    def _onchange_amount_all(self):
        for order in self:
            currency = order.currency_id
            order.amount_tax = currency.round(sum(self._amount_line_tax(line) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal_incl for line in order.lines))
            amount_sub_untaxed = currency.round(sum(line.price_unit*line.qty for line in order.lines))
            order.amount_discount = -1 * currency.round(sum(line.amount_discount for line in order.lines))
            order.amount_sub_total = amount_sub_untaxed
            order.amount_total = amount_untaxed

class EventRetailProduct(models.Model):
    _name = 'event.retail.product'
    _description = 'Event Retail Product'

    @api.depends('qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_price_subtotal(self):
        for rec in self:

            if rec.product_id:
                if rec.discount_type == 'percentage':
                    price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
                else:
                    if rec.discount > rec.price_unit: 
                        raise UserError(_("Discount price should not be greater than unit price!!"))
                    price = rec.price_unit - rec.discount
                # price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
                price_no_discount = 0
                
                rec.price_subtotal = rec.price_subtotal_incl = price * rec.qty
                price_no_discount = rec.price_unit * rec.qty
                rec.amount_discount = price_no_discount - rec.price_subtotal

                total_excluded = 0
                total_included = 0
                for tax in rec.tax_ids:
                    taxes = tax.compute_all(price, rec.currency_id, rec.qty, product=rec.product_id, partner=False)
                    t1 = taxes['total_excluded'] - rec.price_subtotal
                    t2 = taxes['taxes'][0]['amount']
                    total_excluded += t1
                    total_included += t2
                rec.price_subtotal += total_excluded
                rec.price_subtotal_incl += total_included
            else:
                rec.price_subtotal = 0
                rec.price_subtotal_incl = 0


    name = fields.Char()
    # service_categ_id = fields.Many2many('appointment.category', string="Services Category")
    sub_categ_id = fields.Many2many('calendar.appointment.type', string="Sub Category")
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)])
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)
    price_subtotal = fields.Float(string='Subtotal w/o Tax', digits=0, compute='_compute_price_subtotal')
    price_subtotal_incl = fields.Float(string='Subtotal', digits=0, compute='_compute_price_subtotal')
    discount = fields.Float(string='Discount', digits=0, default=0.0)
    order_id = fields.Many2one('pos.order', string='Order Ref', ondelete='cascade')
    tax_ids = fields.Many2many('account.tax', string='Taxes', related="product_id.taxes_id", readonly=False)
    
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', related='product_id.uom_id')
    company_id = fields.Many2one('res.company', string='Venue', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    # full_product_name = fields.Char('Full Product Name')
    event_confirmation_id = fields.Many2one('event.registration.confirmation', string='Order Confirmation')
    # default_product = fields.Boolean()
    amount_discount = fields.Float(string='Discount', digits=0, compute="_compute_discount")
    discount_type = fields.Selection([('flate_rate','Flate Rate'),('percentage','Percentage')], default='percentage', string='Discount Type', required=True)
    total_amt = fields.Float(string="Amount Total",compute="_compute_total_amt")
    discount_amt = fields.Float(string="Discount Amount")
    
    @api.onchange('qty', 'discount', 'price_unit', 'tax_ids', 'discount_type')
    def _onchange_qty(self):
        if self.product_id:
            if self.discount_type == 'percentage':
                price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            else:
                if self.discount > self.price_unit: 
                    raise UserError(_("Discount price should not be greater than unit price!!"))
                price = self.price_unit - self.discount

            price_no_discount = 0
            
            self.price_subtotal = self.price_subtotal_incl = price * self.qty
            price_no_discount = self.price_unit * self.qty
            self.amount_discount = price_no_discount - self.price_subtotal

            total_excluded = 0
            total_included = 0
            for tax in self.tax_ids:
                taxes = tax.compute_all(price, self.currency_id, self.qty, product=self.product_id, partner=False)
                t1 = taxes['total_excluded'] - self.price_subtotal
                t2 = taxes['taxes'][0]['amount']
                total_excluded += t1
                total_included += t2
            self.price_subtotal += total_excluded
            self.price_subtotal_incl += total_included

    @api.depends('discount_type','qty','discount','price_unit','tax_ids')
    def _compute_discount(self):
        for rec in self:
            rec.amount_discount = 0
            if rec.discount_type == 'percentage':
                price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
            else:
                if rec.discount > rec.price_unit: 
                    raise UserError(_("Discount price should not be greater than unit price!!"))
                price = rec.price_unit - rec.discount

            price_no_discount = 0
            with_discount = price * rec.qty
            price_no_discount = rec.price_unit * rec.qty
            rec.amount_discount = price_no_discount - with_discount

# use to calculate amount with qty 24-06-22
    @api.depends('qty','price_unit')
    def _compute_total_amt(self):
        for rec in self:
            rec.total_amt = rec.qty * rec.price_unit




class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    partner_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_partner_rel',
        'wizard_id', 'partner_id', 'Additional Contacts',domain=[])
  
   # used to send the mail and open the invoice preview and also create the pos 27-06-22
    def event_create_pos_mail_send(self):
        active_id = self._context.get('active_id')
        rec_id = self.env["event.registration.confirmation"].browse(active_id)
        if self.model == 'event.registration.confirmation':
            # pos order creation 29-06-22
            rec_id.move_to_pos()
            for rec in self:
                # use to send mail as default flow 29-06-22
                rec.action_send_mail()
                if rec.download_report:
                    return rec_id.proforma_invoice()
