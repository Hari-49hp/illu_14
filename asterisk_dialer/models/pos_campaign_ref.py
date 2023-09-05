# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError

logger = logging.getLogger(__name__)


class Appointment(models.Model):
    _inherit = 'appointment.appointment'

    crm_id = fields.Many2one('crm.lead', string='CRM Reference')
    def write(self,vals):
        result = super(Appointment,self).write(vals)
        if self.quick_remarks_id and self.payment_status_apt != 'paid':
            get_lead_id = self.env['crm.lead'].search([('appointment_id','=',self.id)],limit=1)
            if get_lead_id:
                crm_stage = self.env['crm.stage'].search([('quick_remarks_id','=',self.quick_remarks_id.id)],limit=1)
                get_lead_id.stage_id = crm_stage
        else:
            get_lead_id = self.env['crm.lead'].search([('appointment_id','=',self.id)],limit=1)
            if get_lead_id:
                crm_stage = self.env['crm.stage'].search([('is_won','=',True)],limit=1)
                get_lead_id.stage_id = crm_stage
        return result


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    crm_id = fields.Many2one('crm.lead', string='CRM Refernce')

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        for each in self:
            if each.appt_sale_id and each.appt_sale_id.crm_id and each.appt_sale_id.crm_id.expected_revenue == 0:
                each.sale_apt_id.crm_id.update({
                    'expected_revenue': each.amount_total
                })
            if each.event_reg_id and each.event_reg_id.crm_id and each.event_reg_id.crm_id.expected_revenue == 0:
                each.event_reg_id.crm_id.update({
                    'expected_revenue': each.amount_total
                })        
        return res
