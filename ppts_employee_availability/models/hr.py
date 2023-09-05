from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    @api.model
    def set_current_company_default(self):
        return self.env['res.company'].search([('id', '=', self.env.company.id)]).ids

    def _get_company_allowed_domain(self):
        if self._context.get('allowed_company_ids'): 
            return [('id', 'in', self._context.get('allowed_company_ids'))]

    def _compute_availability_therapist(self):
        for rec in self:
            avail_ids = self.env['availability.availability'].search([('facilitator','=',rec.id),('date_range','=','ongoing'),('available_date','>=',datetime.now().strftime('%Y-%m-%d'))]) #('is_customly_created','=',False) 
            rec.availability_ids = avail_ids.ids

    location = fields.Many2one('venue.venue',string=' Location ')
    location_ids = fields.Many2many('res.company',string='Location ', default=set_current_company_default, domain=_get_company_allowed_domain)
    service_category_ids = fields.Many2many('appointment.category',string='Services Category')
    sequence = fields.Char('Employee Id', default=' ')
    job_position_id = fields.Many2one('hr.job',string="Job ")
    availability_ids = fields.Many2many('availability.availability','availability_availability_availability_ids', string='Availability', compute='_compute_availability_therapist')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(HrEmployeeBase, self).fields_get(allfields, attributes=attributes)
        for field in ['location']:
            if res.get(field):
                res.get(field)['searchable'] = False
                res.get(field)['sortable'] = False
        return res

    @api.model
    def create(self, vals):
        if vals.get('sequence', ' ') == ' ':
            sequence_id = self.env['ir.sequence'].next_by_code('hr.employee') or ' '
            vals['sequence'] = str(sequence_id)
        return super(HrEmployeeBase, self).create(vals)

    def action_show_all_appt(self):
        return {
            'type': 'ir.actions.act_window',
            'name':'Appointments',
            'view_mode': 'tree,form',
            'res_model': 'appointment.line.id',
            'views': [(False, 'tree')],
            'view_id': 'availability_report_tree_viewed',
            'target': 'new',
            'domain': [('therapist_id', '=', self.id)],
        }

    def action_show_all_avaialbles(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Availabilities',
            'view_mode': 'tree,form',
            'res_model': 'availability.availability',
            'domain': [('facilitator', '=', self.id)],
        }

    def create_availability(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Availabilities',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'availability.availability',
            'context': {'default_facilitator': self.id,'default_employee_form':True},
        }

    
