from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import calendar

class ClientView(models.Model):
	_name = 'client.view'
	_description="ClientView"

	name = fields.Many2one('res.partner', string="Client")
	day = fields.Char(string="Day", compute="_compute_weekday")
	date = fields.Date(string="Date")
	time = fields.Char(string='Time')
	visit_serv_categ_id = fields.Many2one('appointment.category', string="Visit Service Category")
	visit_type_id = fields.Many2one('appointment.category', string="Visit Type")
	pricing_option = fields.Char("Pricing Options", default="n/a")
	type_id = fields.Many2one('calendar.appointment.type', string="Type")
	expiry_date = fields.Date(string='Exp. Date')
	visit_rem = fields.Integer(string='Visit Rem')
	staff = fields.Many2one('res.users', string="Staff")
	visit_location = fields.Many2one('res.company', string="Visit Location")
	staff_paid = fields.Selection([('yes', 'Yes'),('no', 'No')],
                                    string='Staff Paid', compute="_compute_staff_paid")
	late_cancel = fields.Selection([('yes', 'Yes'),('no', 'No')],
                                    string='Late Cancel', compute="_compute_late_cancel")
	no_show = fields.Selection([('yes', 'Yes'),('no', 'No')],
                                    string='No- show', compute="_compute_no_show")
	booking_mode = fields.Selection([('online', 'Website'),('direct', 'Backend')],
                                    string='Booking Method')
	payment_method = fields.Char(string="Payment Method", compute="_compute_payment_method")
	pos_id = fields.Many2one('pos.order')
	apt_id = fields.Many2one('appointment.appointment')

	@api.depends('apt_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.apt_id.state == 'cancel':
				rec.late_cancel = 'yes'
			else:
				rec.late_cancel = 'no'

	@api.depends('apt_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.apt_id.state == 'no_show':
				rec.no_show = 'yes'
			else:
				rec.no_show = 'no'

	@api.depends('apt_id')
	def _compute_staff_paid(self):
		for rec in self:
			if rec.apt_id.payment_status_apt == 'paid':
				rec.staff_paid = 'yes'
			else:
				rec.staff_paid = 'no'

	def _compute_payment_method(self):
		for rec in self:
			cash = 0.00
			apt = self.env['appointment.appointment'].search(
				[('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
			pos = self.env['pos.order'].search([('appt_sale_id', 'in', apt.ids)])
			print(pos, "PoS ID")
			for payment in pos.payment_ids:
				print(payment.payment_method_id.name)
				if payment.payment_method_id.name == 'Cash':
					cash = payment.payment_method_id.name
					rec.payment_method = cash
				elif payment.payment_method_id.name == 'Bank':
					rec.payment_method = bank
				elif payment.payment_method_id.name == 'Net Banking':
					rec.payment_method = net
				else:
					rec.payment_method = 'None'

	@api.depends('date')
	def _compute_weekday(self):
		for rec in self:
			if rec.date:
				day = fields.Datetime.from_string(rec.date)
				rec.day = calendar.day_name[day.weekday()]

					
class AttendanceServiceCategory(models.Model):
	_name = "attendance.service.category"
	_description = "AttendanceServiceCategory"

	name = fields.Many2one('res.partner', string="Client")
	day = fields.Char(string="Day")
	date = fields.Date(string="Date", related="apt_id.booking_date")
	time = fields.Char(string='Time')
	visit_serv_categ_id = fields.Many2one('appointment.category', string="Visit Service Category", related="apt_id.du_service_categ_id")
	visit_type_id = fields.Many2one('appointment.category', string="Visit Type")
	pricing_option = fields.Char("Pricing Options", default="n/a")
	type_id = fields.Many2one('calendar.appointment.type', string="Type")
	expiry_date = fields.Date(string='Exp. Date')
	visit_rem = fields.Integer(string='Visit Rem')
	staff = fields.Many2one('res.users', string="Staff")
	visit_location = fields.Many2one('res.company', string="Visit Location")
	staff_paid = fields.Selection([('yes', 'Yes'),('no', 'No')],
                                    string='Staff Paid', compute="_compute_staff_paid")
	late_cancel = fields.Selection([('yes', 'Yes'),('no', 'No')],
                                    string='Late Cancel', compute="_compute_late_cancel")
	no_show = fields.Selection([('yes', 'Yes'),('no', 'No')],
                                    string='No- show', compute="_compute_no_show")
	booking_mode = fields.Selection([('online', 'Website'),('direct', 'Backend')],
                                    string='Booking Method')
	payment_method = fields.Selection([('cash', 'Cash'),('net', 'Net Banking'),
        ('bank', 'Bank')], string="Payment Method", compute="_compute_payment_method")
	pos_id = fields.Many2one('pos.order')
	apt_id = fields.Many2one('appointment.appointment')


	def _compute_payment_method(self):
		for rec in self:
			apt = self.env['appointment.appointment'].search(
				[('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
			pos = self.env['pos.order'].search([('appt_sale_id', 'in', apt.ids)])
			print(pos, "PoS ID")
			for payment in pos.payment_ids:
				print(payment.payment_method_id.name)
				if payment.payment_method_id.name == 'Cash':
					print('True')
					rec.payment_method = 'cash'
				elif payment.payment_method_id.name == 'Bank':
					rec.payment_method = 'bank'
				elif payment.payment_method_id.name == 'Net Banking':
					rec.payment_method = 'net'


	@api.depends('apt_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.apt_id.state == 'cancel':
				rec.late_cancel = 'yes'
			else:
				rec.late_cancel = 'no'

	@api.depends('apt_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.apt_id.state == 'no_show':
				rec.no_show = 'yes'
			else:
				rec.no_show = 'no'

	@api.depends('apt_id')
	def _compute_staff_paid(self):
		for rec in self:
			if rec.apt_id.payment_status_apt == 'paid':
				rec.staff_paid = 'yes'
			else:
				rec.staff_paid = 'no'

class AttendanceSummary(models.Model):
	_name = "attendance.summary"
	_description="AttendanceSummary"

	def _get_company_allowed_domain(self):
		if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

	name = fields.Many2one('res.partner', string="Client")
	day = fields.Char(string="Day")
	date = fields.Date(string="Date")

	time = fields.Char(string='Time')
	visit_serv_categ_id = fields.Char( string="Visit Service Category") #Many2one('product.category',
	staff_id = fields.Many2one('res.users', string="Staff")
	type_id = fields.Char( string="Type")
	visit_type_id = fields.Char( string="Visit Type") #Many2one('product.category',
	visit_location = fields.Many2one('res.company', string="Visit Location")
	paid_client = fields.Integer(string="Paid Clients", compute="_compute_paid")
	comp_client = fields.Integer(string="Comp Clients", compute="_compute_comp")
	late_cancel = fields.Integer(string="Late Cancel", compute="_compute_late_cancel")
	no_show = fields.Integer(string="No Show", compute="_compute_no_show")
	online_booking = fields.Integer(string="Online Bookings", compute='_compute_mode')
	members = fields.Integer(string="Members")
	members_revenue = fields.Monetary(currency_field='currency_id', string='Members Revenue')
	total_revenue = fields.Monetary(currency_field='currency_id', string='Total Revenue')

	company_id = fields.Many2one('res.company', string='Venue', change_default=True,
								 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
								 required=False)
	currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
	location_id = fields.Many2one('res.company', string='Location')
	pos_id = fields.Many2one('pos.order')
	sale_id = fields.Many2one('appointment.appointment')


	@api.depends('sale_id')
	def _compute_paid(self):
		for rec in self:
			if rec.sale_id.payment_status_apt == 'paid':
				rec.paid_client = 1
			else:
				rec.paid_client = 0

	@api.depends('sale_id')
	def _compute_comp(self):
		for rec in self:
			if rec.sale_id.state  == 'done':
				rec.comp_client = 1
			else:
				rec.comp_client = 0

	@api.depends('sale_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.sale_id.state == 'cancel':
				rec.late_cancel = 1
			else:
				rec.late_cancel = 0

	@api.depends('sale_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.sale_id.state == 'no_show':
				rec.no_show = 1
			else:
				rec.no_show = 0

	@api.depends('sale_id')
	def _compute_mode(self):
		for rec in self:
			if rec.sale_id.booking_mode == 'online':
				rec.online_booking = 1
			else:
				rec.online_booking = 0


class AttendanceStaffMember(models.Model):
	_name = "attendance.staff"
	_description="AttendanceStaffMember"

	def _get_company_allowed_domain(self):
		if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

	name = fields.Char()
	day = fields.Char(string="Day")
	date = fields.Date(string="Date")
	time = fields.Char(string='Time')
	staff_id = fields.Many2one('res.users', string="Staff")

	client = fields.Many2one('res.partner', string="Client")
	visit_serv_categ_id = fields.Char( string="Visit Service Category") #Many2one('product.category'
	visit_type_id = fields.Char( string="Visit Type") #Many2one('product.category'
	pricing_option_id = fields.Char( string="Pricing Option")  #Many2one('calendar.appointment.type'
	expiry_date = fields.Date(string='Exp. Date')
	visit_rem = fields.Integer(string='Visit Rem')
	visit_location = fields.Many2one('res.company', string="Visit Location")
	staff_paid = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='Staff Paid' , compute='_compute_staff_paid')
	late_cancel = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='Late Cancel', compute='_compute_late_cancel')
	no_show = fields.Selection([('yes', 'Yes'), ('no', 'No')],string='No- show' , compute='_compute_no_show')
	booking_mode = fields.Selection([('online', 'Website'), ('direct', 'Backend')],string='Booking Method')
	payment_method = fields.Many2many('pos.payment.method', compute='_get_pay_method')
	revenue = fields.Monetary(currency_field='currency_id', string='Rev.per Visit')

	company_id = fields.Many2one('res.company', string='Venue', change_default=True,
								 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
								 required=False)
	currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
	location_id = fields.Many2one('res.company', string='Location')
	pos_id = fields.Many2one('pos.order')
	apt_id = fields.Many2one('appointment.appointment')



	@api.depends('apt_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.apt_id.state == 'cancel':
				rec.late_cancel = 'yes'
			else:
				rec.late_cancel = 'no'

	@api.depends('apt_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.apt_id.state == 'no_show':
				rec.no_show = 'yes'
			else:
				rec.no_show = 'no'

	@api.depends('apt_id')
	def _compute_staff_paid(self):
		for rec in self:
			if rec.apt_id.payment_status_apt == 'paid':
				rec.staff_paid = 'yes'
			else:
				rec.staff_paid = 'no'

	def _get_pay_method(self):
		for rec in self:
			apt = self.env['appointment.appointment'].search(
				[('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
			pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
			rec.payment_method = pos.payment_ids.payment_method_id.ids

class AttendanceDate(models.Model):
	_name = "attendance.date"
	_description ="AttendanceDate"

	def _get_company_allowed_domain(self):
		if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

	name = fields.Char()
	day = fields.Char(string="Day")
	date = fields.Date(string="Date")
	time = fields.Char(string='Time')

	client = fields.Many2one('res.partner', string="Client")
	visit_serv_categ_id = fields.Char(string="Visit Service Category")  # Many2one('product.category'
	visit_type_id = fields.Char(string="Visit Type")  # Many2one('product.category'
	pricing_option_id = fields.Char(string="Pricing Option")  # Many2one('calendar.appointment.type'
	expiry_date = fields.Date(string='Exp. Date')
	visit_rem = fields.Integer(string='Visit Rem')
	visit_location = fields.Many2one('res.company', string="Visit Location")
	staff_id = fields.Many2one('res.users', string="Staff")
	staff_paid = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Staff Paid', compute='_compute_staff_paid')
	late_cancel = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Late Cancel', compute='_compute_late_cancel')
	no_show = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='No- show', compute='_compute_no_show')
	booking_mode = fields.Selection([('online', 'Website'), ('direct', 'Backend')], string='Booking Method')
	payment_method = fields.Many2many('pos.payment.method', compute='_get_pay_method')
	revenue = fields.Monetary(currency_field='currency_id', string='Rev.per Visit')

	company_id = fields.Many2one('res.company', string='Venue', change_default=True,
								 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
								 required=False)
	currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
	location_id = fields.Many2one('res.company', string='Location')
	pos_id = fields.Many2one('pos.order')
	apt_id = fields.Many2one('appointment.appointment')

	@api.depends('apt_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.apt_id.state == 'cancel':
				rec.late_cancel = 'yes'
			else:
				rec.late_cancel = 'no'

	@api.depends('apt_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.apt_id.state == 'no_show':
				rec.no_show = 'yes'
			else:
				rec.no_show = 'no'

	@api.depends('apt_id')
	def _compute_staff_paid(self):
		for rec in self:
			if rec.apt_id.payment_status_apt == 'paid':
				rec.staff_paid = 'yes'
			else:
				rec.staff_paid = 'no'

	def _get_pay_method(self):
		for rec in self:
			apt = self.env['appointment.appointment'].search(
				[('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
			pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
			rec.payment_method = pos.payment_ids.payment_method_id.ids

class AttendanceVisitType(models.Model):
	_name = "attendance.visit.type"
	_description ="AttendanceVisitType"

	def _get_company_allowed_domain(self):
		if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

	name = fields.Char()
	day = fields.Char(string="Day")
	date = fields.Date(string="Date")
	time = fields.Char(string='Time')
	visit_type_id = fields.Char(string="Visit Type")  # Many2one('product.category'

	client = fields.Many2one('res.partner', string="Client")
	visit_serv_categ_id = fields.Char(string="Visit Service Category")  # Many2one('product.category'
	pricing_option_id = fields.Char(string="Pricing Option")  # Many2one('calendar.appointment.type'
	expiry_date = fields.Date(string='Exp. Date')
	visit_rem = fields.Integer(string='Visit Rem')
	visit_location = fields.Many2one('res.company', string="Visit Location")
	staff_id = fields.Many2one('res.users', string="Staff")
	staff_paid = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Staff Paid', compute='_compute_staff_paid')
	late_cancel = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Late Cancel', compute='_compute_late_cancel')
	no_show = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='No- show', compute='_compute_no_show')
	booking_mode = fields.Selection([('online', 'Website'), ('direct', 'Backend')], string='Booking Method')
	payment_method = fields.Many2many('pos.payment.method', compute='_get_pay_method')
	revenue = fields.Monetary(currency_field='currency_id', string='Rev.per Visit')

	company_id = fields.Many2one('res.company', string='Venue', change_default=True,
								 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
								 required=False)
	currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
	location_id = fields.Many2one('res.company', string='Location')
	pos_id = fields.Many2one('pos.order')
	apt_id = fields.Many2one('appointment.appointment')

	@api.depends('apt_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.apt_id.state == 'cancel':
				rec.late_cancel = 'yes'
			else:
				rec.late_cancel = 'no'

	@api.depends('apt_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.apt_id.state == 'no_show':
				rec.no_show = 'yes'
			else:
				rec.no_show = 'no'

	@api.depends('apt_id')
	def _compute_staff_paid(self):
		for rec in self:
			if rec.apt_id.payment_status_apt == 'paid':
				rec.staff_paid = 'yes'
			else:
				rec.staff_paid = 'no'

	def _get_pay_method(self):
		for rec in self:
			apt = self.env['appointment.appointment'].search(
				[('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
			pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
			rec.payment_method = pos.payment_ids.payment_method_id.ids

class AttendanceNoShowLateCancel(models.Model):
	_name = "attendance.noshow.cancels"
	_description ="AttendanceNoShowLateCancel"

	def _get_company_allowed_domain(self):
		if self._context.get('allowed_company_ids'): return [('id', 'in', self._context.get('allowed_company_ids'))]

	name = fields.Char()
	day = fields.Char(string="Day")
	date = fields.Date(string="Date")
	time = fields.Char(string='Time')
	visit_type_id = fields.Char(string="Visit Type")  # Many2one('product.category'

	client = fields.Many2one('res.partner', string="Client")
	visit_serv_categ_id = fields.Char(string="Visit Service Category")  # Many2one('product.category'
	pricing_option_id = fields.Char(string="Pricing Option")  # Many2one('calendar.appointment.type'
	expiry_date = fields.Date(string='Exp. Date')
	visit_rem = fields.Integer(string='Visit Rem')
	visit_location = fields.Many2one('res.company', string="Visit Location")
	staff_id = fields.Many2one('res.users', string="Staff")
	staff_paid = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Staff Paid', compute='_compute_staff_paid')
	late_cancel = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Late Cancel', compute='_compute_late_cancel')
	no_show = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='No- show', compute='_compute_no_show')
	booking_mode = fields.Selection([('online', 'Website'), ('direct', 'Backend')], string='Booking Method')
	payment_method = fields.Many2many('pos.payment.method', compute='_get_pay_method')
	revenue = fields.Monetary(currency_field='currency_id', string='Rev.per Visit')

	company_id = fields.Many2one('res.company', string='Venue', change_default=True,
								 default=lambda self: self.env.company, domain=_get_company_allowed_domain,
								 required=False)
	currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
	location_id = fields.Many2one('res.company', string='Location')
	pos_id = fields.Many2one('pos.order')
	apt_id = fields.Many2one('appointment.appointment')

	@api.depends('apt_id')
	def _compute_late_cancel(self):
		for rec in self:
			if rec.apt_id.state == 'cancel':
				rec.late_cancel = 'yes'
			else:
				rec.late_cancel = 'no'

	@api.depends('apt_id')
	def _compute_no_show(self):
		for rec in self:
			if rec.apt_id.state == 'no_show':
				rec.no_show = 'yes'
			else:
				rec.no_show = 'no'

	@api.depends('apt_id')
	def _compute_staff_paid(self):
		for rec in self:
			if rec.apt_id.payment_status_apt == 'paid':
				rec.staff_paid = 'yes'
			else:
				rec.staff_paid = 'no'

	def _get_pay_method(self):
		for rec in self:
			apt = self.env['appointment.appointment'].search(
				[('state', 'in', ['new', 'confirm', 'arrive', 'no_show', 'ongoing', 'done', 'cancel'])])
			pos = self.env['pos.order'].search([('appt_sale_id', '=', rec.apt_id.id)])
			rec.payment_method = pos.payment_ids.payment_method_id.ids

