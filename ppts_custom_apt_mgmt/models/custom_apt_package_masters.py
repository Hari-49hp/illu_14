from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AppointmentPackage(models.Model):
    _name = 'appointment.package'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment Package'
    _rec_name = 'name'

    name = fields.Char('Package Name', tracking=True)
    code = fields.Char('Code', tracking=True)
    notes = fields.Text('Internal Note', tracking=True)
    discount = fields.Float(string='Discount %', copy=False, tracking=True)
    sell_online = fields.Boolean(string='Sell Online',default=False, tracking=True)
    online_description = fields.Html('Online description', tracking=True)
    members_only_ids = fields.Char('Members only', tracking=True)
    location_ids = fields.Many2many('res.company',string='Locations', tracking=True)
    is_discontinued = fields.Boolean(string='Is Discontinued?',default=False, tracking=True)
    package_cancel_charge_ids = fields.One2many('package.cancel.charge', 'package_id', string='Cancellation Charges')
    ser_categ = fields.Many2many('appointment.category',string="Service Category")
    sub_categ = fields.Many2many('calendar.appointment.type',string="Sub Category")
    qty_count = fields.Integer('Qty Count')
    product_id = fields.Many2one('product.product',string='Product')
    product_price = fields.Float('Product Price')
    package_qty = fields.Float('Quantity')
    sequence = fields.Integer('Sequence')


    #new product will be created for every package
    @api.model
    def create(self, vals):
        res = super(AppointmentPackage, self).create(vals)

        product_id = self.env['product.product'].sudo().create({
                        'name': res.name,
                        'default_code': res.name,
                        'type': 'service',
                        'invoice_policy': 'order',
                        'supplier_taxes_id': False,
                        'taxes_id': False,
                        'sale_ok': True,
                        'available_in_pos': True,
                        'package_product': True,
                        'purchase_ok': False,
                        'list_price': res.product_price,
                        'company_id':False
                    })
        res.product_id = product_id.id
        return res
    
    def write(self,vals):
        res = super(AppointmentPackage, self).write(vals)
        if self.product_id:
            self.product_id.list_price = self.product_price
        else:
            product_id = self.env['product.product'].sudo().create({
                        'name': self.name,
                        'default_code': self.name,
                        'type': 'service',
                        'invoice_policy': 'order',
                        'supplier_taxes_id': False,
                        'taxes_id': False,
                        'sale_ok': True,
                        'purchase_ok': False,
                        'available_in_pos': True,
                        'package_product': True,
                        'list_price': self.product_price,
                        'company_id': False
                    })
            self.product_id = product_id.id
            
        return res

    #used to update qty in lines
    @api.onchange('package_qty')
    def _onch_package_qty(self):
        for res in self.package_cancel_charge_ids:

            res.package_of_total = self.package_qty

class PackageCancellationCharge(models.Model):
    _name = 'package.cancel.charge'
    _description = 'Package Cancel Charge'
    _rec_name = 'package_of_total'

    package_id = fields.Many2one('appointment.package',string='Package Id')
    package_of_cancel = fields.Integer('Cancelled Services',required=True)
    domain = fields.Selection([('equal','='),('is_not_equal','is not ='),('greater_than','>'),('less_than','<'),('greater_than_equal','> ='),('less_than_equal','< =')],string='Domain',required=True)
    package_of_total = fields.Float('Total Packages',readonly=True)#required=True) #,related="package_id.qty_count"
    original_rate = fields.Float('Original Rate.%')
    original_rate_charge = fields.Boolean('Original Rate Price')

    # @api.onchange('original_rate_charge')
    def _onch_original_rate_charge(self):
        if self.original_rate_charge:
            self.original_rate=0.0

    @api.onchange('domain')
    def _onch_domain(self):
        for res in self:

            res.package_of_total = self.package_id.package_qty

