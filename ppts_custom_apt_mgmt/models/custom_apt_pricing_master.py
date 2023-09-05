from odoo import api, fields, models, _

ACCOUNT_DOMAIN = "['&', '&','&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"

class AppointmentPricing(models.Model):
    _inherit = ['product.template']

    appointment_id = fields.Many2one('calendar.appointment.type', string="Appointment Type")

    product_used = fields.Selection([
        ('appointments', 'Appointment'),
        ('event', 'Event'),
        ('none', 'None'),
    ], string='Pricing Option for',
        tracking=True,
        default='none')


    product_name = fields.Char('Product Name',
                               tracking=True, related="name",
                               help='When clients or staff are viewing a list of pricing options, you can help them pick the right one by including the number of sessions and being specific in the name (e.g., 1 Month Unlimited, 5 Private Sessions).')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    price = fields.Float('Price',
                         tracking=True,
                         help="Please enter a price of this pricing option if purchased in store (does not affect Online Store)")
    sell_online = fields.Boolean(string='Sell Online',
                                 default=False,
                                 tracking=True,
                                 help="Allow clients to purchase this pricing option online and on their mobile devices.")
    is_taxable = fields.Boolean(string='Add VAT?', default=False,
                                tracking=True,
                                help="Add VAT for this pricing.")
    online_store_link = fields.Char('Online Store Link',
                                    tracking=True,
                                    help="Online Store Link."
                                    )

    expiry_date = fields.Date('Expires', tracking=True,required=True, help="How long does the client have to use this pricing option before it expires?")

    # expiry_type = fields.Selection([
    #     ('type_month', 'Month'),
    #     ('type_year', 'Year')], string='Type of Expire?',required=True)

    expiry_duration = fields.Integer('Expires', tracking=True,help="When would you like this pricing option to activate for your clients?")

    expiry_duration_unit = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months')], string='Expire Unit',
        tracking=True,
        default='months',
        help="When would you like this pricing option to activate for your clients?"
    )


    #Date field is not need

    expiry_after = fields.Selection([
        ('type_sale_date', 'the sale date'),
        ('type_client_visit', "the date of the client's first visit")],
        string='Type of Expire?',
        required=True,
        default='type_sale_date',
        help="When would you like this pricing option to activate for your clients?"
    )

    session_type = fields.Selection([
            ('type_single', 'Sinlge'),
            ('type_multi', 'Multiple'),
            ('type_unlimit', 'Unlimited'),
            ], string='Type of Sessions?',required=True, tracking=True,
            default='type_single',
            help="Pricing option with limited visits- Typically expires when visits have been used up. Pricing option with unlimited visits - typically expires based on time. Membership - expires based on time or visits and receives special membership benefits. Note: Memberships must first be created first under Manager Tools => Membership Setup."
        )

    session_limit = fields.Integer('Number of Sessions', tracking=True,
            help="How many visits does the client receive when they purchase this pricing option?"
            )

    introductory_offer = fields.Selection([
            ('type_no', 'No'),
            ('type_new_only', 'Yes, for new clients only'),
            ('type_all', 'Yes, for new and existing clients'),
            ], string='Is this an Introductory Offer? (limit of 1 per client)',
        required=True,
        tracking=True,
        default='type_no',
        help="Limits clients to purchasing this item one time."
    )

    revenue_category_id = fields.Many2one('appointment.revenue', string='Revenue Category',
                                          copy=False,
                                          tracking=True,
                                          #domain=ACCOUNT_DOMAIN,
                                          help="All pricing options are connected to a revenue category so that you can easily report on how services are doing in terms of sales. It's best if your revenue category name matches your service category name.")

    show_additional = fields.Boolean(string='Additional Information', default=False,
                                tracking=True)

    membership_category_id = fields.Char(string='Membership', copy=False, tracking=True,
                                         help="Does a client become a member when they purchase this pricing option? If so, select a membership below.")

    purchase_restrict = fields.Boolean(string='Only allow clients to purchase this in a contract or package?',
                                       default=False,
                                       tracking=True,
                                       help="Can this pricing option only be purchased as part of a contract or a package?")
    advance_settings = fields.Boolean(string='Need to set up advanced settings (e.g., members discounts, restrictions)? ', default=False, tracking=True)


    is_commission_product = fields.Boolean(string='Commission Product')
    commission_type = fields.Selection([('percentage', 'Percentage'),('fixed_price', 'Fixed Price'),], string='Commission Price Type', default='percentage')
    commission_percentage = fields.Float(string='Commission')
    commission_fixed_price = fields.Float(string='Commission')


class ApointmentRevenuCateg(models.Model):
    _name = 'appointment.revenue'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment Revenue '
    _rec_name = 'name'

    name = fields.Char('Name', tracking=True)
    code = fields.Char('Code', invisible=True)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company, required=True, tracking=True)
    account_id = fields.Many2one('account.account', string='Ledger Category', copy=False, tracking=True, domain=ACCOUNT_DOMAIN, help="All pricing options are connected to a revenue category so that you can easily report on how services are doing in terms of sales. It's best if your revenue category name matches your service category name.")
    type_appointment = fields.Selection([('type_online', 'Online'), ('type_onsite', 'Onsite')], string='Appointment Platform', default='type_onsite')
    booking_mode = fields.Selection([('online', 'Website'), ('direct', 'Backend')], string='Mode of Appointment?', default='direct', required=True, tracking=True)
    notes = fields.Text('Internal Note', tracking=True)

