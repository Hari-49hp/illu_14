from odoo import api, fields, models


class CustomAppointments(models.Model):
    _inherit = 'availability.availability'

    service_categ_domain = fields.Boolean(string="Edit Service Details")
    service_categ_id = fields.Many2many('appointment.category', string="Services Category")
    sub_categ_id = fields.Many2many('calendar.appointment.type', string="Sub Category")
    services_length = fields.Char(string='Service Categories', compute='_compute_services_length')
    sub_categ_name = fields.Text(string='Sub Category', compute='_compute_sub_categ_name')
    
    @api.depends('sub_categ_id')
    def _compute_sub_categ_name(self):
        for rec in self:
            data_list = []
            rec.sub_categ_name = ''
            if rec.sub_categ_id:
                sub_cate_ids = self.env['calendar.appointment.type'].search([('id', 'in', rec.sub_categ_id.ids)])
                for line in sub_cate_ids:
                    data_list.append(line.name)
                    rec.sub_categ_name = ", ".join((
                            data_list
                        ))
            else:
                rec.sub_categ_name = ''

    @api.depends('service_categ_id')
    def _compute_services_length(self):
        for rec in self:
            if rec.service_categ_id:
                if len(rec.service_categ_id) > 1:
                    rec.services_length = str(len(rec.service_categ_id)) + ' Services'
                elif len(rec.service_categ_id) == 1:
                    rec.services_length = rec.service_categ_id[0].name
                else:
                    rec.services_length = ''
            else:
                rec.services_length = ''

    @api.onchange('facilitator', 'service_categ_id', 'service_categ_domain')
    def _onchange_service_ids_domain(self):
        lstt = []
        resp = {'domain': {'service_categ_id': "[('id', 'not in', False)]"}}
        if self.facilitator:
            for i in self.facilitator.pay_rate_ids:
                if i.service_category_type_id.id not in lstt: 
                    lstt.append(i.service_category_type_id.id)
        resp['domain']['service_categ_id'] = "[('id', 'in', %s)]" % lstt
        return resp

    @api.onchange('facilitator', 'service_categ_id', 'service_categ_domain')
    def _onchange_sub_service_ids_domain(self):
        lst = []
        res = {'domain': {'sub_categ_id': "[('id', 'not in', False)]"}}
        if self.facilitator and self.service_categ_id:
            for i in self.facilitator.pay_rate_ids:
                if i.appoinment_type_id.id not in lst and i.service_category_type_id.id in self.service_categ_id.ids: 
                    lst.append(i.appoinment_type_id.id)
        res['domain']['sub_categ_id'] = "[('id', 'in', %s)]" % lst
        sub_categ_ids = list(set(self.sub_categ_id.ids) & set(lst))
        self.sub_categ_id = [(6, False, sub_categ_ids)]
        return res

    @api.onchange('availability')
    def _onchange_availability_null(self):
        if self.availability != 'available':
            self.service_categ_id = False
            self.sub_categ_id = False

    @api.onchange('facilitator')
    def _onchange_appt_service_category_ids(self):
        if self.facilitator:
            lst = []
            if self.availability == 'available':
                for i in self.facilitator.pay_rate_ids:
                    if i.service_category_type_id:
                        if i.service_category_type_id.id not in lst:
                            lst.append(i.service_category_type_id.id)
                self.update({
                    'service_categ_id': [(6, 0, lst)],
                    'sub_categ_id': False,
                })
            else:
                self.service_categ_id = False
                self.sub_categ_id = False

    # Onchange for update the service_categ_id in line item
    @api.onchange('service_categ_id')
    def change_app_line_id(self):
        if self.app_line_id:
            for rec in self.app_line_id:
                rec.service_categ_id = self.service_categ_id

    # Onchange for update the sub_categ_id in line item
    @api.onchange('sub_categ_id')
    def change_sub_categ_id(self):
        if self.app_line_id:
            for rec in self.app_line_id:
                rec.service_categ_id = self.service_categ_id
                rec.sub_categ_id = self.sub_categ_id


class AvailabilityServiceLine(models.Model):
    _inherit = 'availability.service.line'
    _rec_name = 'service_id'

    service_id = fields.Many2one('appointment.category', string="Services", required=True)


class AvailabilityAvailabilityLine(models.Model):
    _inherit = 'availability.availability.line'

    service_categ_id = fields.Many2many('appointment.category', string="Services Category")
    sub_categ_id = fields.Many2many('calendar.appointment.type', string="Sub Category")

    @api.onchange('app_id', 'facilitator', 'service_categ_id', 'start_time', 'end_time', 'date_app', 'is_services')
    def _onchange_service_ids_domain(self):
        lstt = []
        resp = {'domain': {'service_categ_id': "[('id', 'not in', False)]"}}
        if self.facilitator:
            for i in self.facilitator.pay_rate_ids:
                if i.service_category_type_id.id not in lstt: 
                    lstt.append(i.service_category_type_id.id)
        resp['domain']['service_categ_id'] = "[('id', 'in', %s)]" % lstt
        return resp

    @api.onchange('app_id', 'facilitator', 'service_categ_id', 'start_time', 'end_time', 'date_app', 'is_services')
    def _onchange_sub_service_ids_domain(self):
        lst = []
        res = {'domain': {'sub_categ_id': "[('id', 'not in', False)]"}}
        if self.facilitator and self.service_categ_id:
            for i in self.facilitator.pay_rate_ids:
                if i.appoinment_type_id.id not in lst and i.service_category_type_id.id in self.service_categ_id.ids: 
                    lst.append(i.appoinment_type_id.id)
        res['domain']['sub_categ_id'] = "[('id', 'in', %s)]" % lst
        sub_categ_ids = list(set(self.sub_categ_id.ids) & set(lst))
        self.sub_categ_id = [(6, False, sub_categ_ids)]
        return res

    @api.onchange('is_services')
    def _onchange_is_services(self):

        print(self.facilitator, "OOOOOOOOOOO")


class AvailabilitySetdraft(models.Model):
    _inherit = 'availability.setdraft'

    review_appointment_ids = fields.Many2many('appointment.appointment',
                                              'appointment_appointment_review_availability_ids', string="Appointments")
