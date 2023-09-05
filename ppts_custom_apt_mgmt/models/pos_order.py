from odoo import api, fields, models, _

class PosOrder(models.Model):
    _inherit = 'pos.order'

    appt_sale_id = fields.Many2one('appointment.appointment',string="appointment")
    session_type = fields.Selection([
        ('type_single', 'Single Session'),
        ('type_package', 'Package Session')], string='Type Of Session?', default='type_single', required=True)
    booking_type = fields.Selection([
        ('facilitator', 'Facilitator'),
        ('appointment', 'Appointment'),
        ('room', 'Room'), ('event', 'Event')
    ], string='Booking Type', copy=False)
    sale_type_for = fields.Selection([('appointment','Appointment'),('event','Event'),('other','Other')], default='other')
    apt_booking_date = fields.Date(string='Appointment Date')
    apt_booked_by = fields.Many2one('res.users',string='Sales Rep')
    commission_recipient = fields.Boolean('Commission Recipient', default=True)

    def action_pos_order_invoice(self):
        res = super(PosOrder, self).action_pos_order_invoice()
        for rec in self:
            if rec.commission_recipient == True:
                for i in rec.lines:
                    if i.appointment_set_id:
                        if i.commission_recipient == 'therapist':
                            self.env['employee.commission'].create({
                                'employee_id': i.appointment_set_id.therapist_id.id,
                                'sale_id': rec.id,
                                'appointment_id': i.appointment_set_id.id,
                                'commission': i.therapist_commission,
                            })
                        elif i.commission_recipient == 'sale_person':
                            emp_id = self.env['hr.employee'].search([('user_id','=',i.appointment_set_id.sales_rep_id.id)],limit=1)
                            self.env['employee.commission'].create({
                                'employee_id': emp_id.id,
                                'sale_id': rec.id,
                                'appointment_id': i.appointment_set_id.id,
                                'commission': i.therapist_commission,
                            })
        return res 

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    apt_service_category = fields.Many2one('appointment.category', string='Service Category')
    appt_sale_id = fields.Many2one('appointment.appointment',string="appointment",related="order_id.appt_sale_id",readonly=False)
    appointment_set_id = fields.Many2one('appointment.appointment',string="Appointment",related="order_id.appt_sale_id")
    session_remaining = fields.Char(string="Session Remaining",related="appt_sale_id.session_remaining")
    appt_line_id = fields.Many2one('appointment.line.id',string="appointment lines id")
    session_type = fields.Selection([
        ('type_single', 'Single Session'),
        ('type_package', 'Package Session')], string='Type Of Session?', default='type_single', required=True)
    booking_type = fields.Selection([
        ('facilitator', 'Facilitator'),
        ('appointment', 'Appointment'),
        ('room', 'Room'), ('event', 'Event')
    ], string='Booking Type', copy=False)
    
    commission_type = fields.Selection(string='Commission Recipient ', related='product_id.commission_type', store=True, readonly=False)
    therapist_commission_type = fields.Float('Percentage or Price', compute='_compute_therapist_commission_type', readonly=False)
    therapist_commission = fields.Float('Commission', compute='_compute_therapist_commission', readonly=False)
    commission_recipient = fields.Selection([('none', 'None'),('sale_person', 'Sale Person'),('therapist', 'Therapist')], string='Commission Recipient', default='none')
    default_product = fields.Boolean()

    @api.depends('product_id','commission_type')
    def _compute_therapist_commission_type(self):
        for rec in self:
            if rec.product_id.commission_type == 'percentage':
                rec.therapist_commission_type = rec.product_id.commission_percentage
            else:
                rec.therapist_commission_type = rec.product_id.commission_fixed_price
    
    @api.depends('product_id','commission_type','therapist_commission_type','price_unit')
    def _compute_therapist_commission(self):
        for rec in self:
            rec.therapist_commission = 0.0
            if rec.commission_type == 'percentage':
                if rec.therapist_commission_type < rec.price_subtotal:
                    rec.therapist_commission = rec.price_subtotal * rec.therapist_commission_type / 100
            else:
                if rec.therapist_commission_type < rec.price_subtotal:
                    rec.therapist_commission = rec.therapist_commission_type