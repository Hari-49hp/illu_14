from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import *
import logging

_logger = logging.getLogger(__name__)

# Appointments & Booking
class CustomAppointments(models.Model):
    _inherit = 'appointment.appointment'

    type_appointment = fields.Selection([('type_online', 'Online'), ('type_onsite', 'Onsite')],
                                        string='Mode of Appointment?', default='type_onsite')

    apt_partner_historys = fields.Many2many('appointment.line.id',
                                           'appointment_line_apt_partner_historys',
                                           'apt_history_changes', string='History',store=True)

    parent_id = fields.Many2one('appointment.appointment', string='Appointment-Package')
    apt_package_parent_id = fields.Many2one('appointment.appointment', string='Appointment-Package ')
    package_line_id = fields.Many2one('appointment.line.id', string='Package Line ID')

    cancel_reason_id = fields.Many2one('appointment.cancel.reason', string='Cancel Reason')
    cancel_note = fields.Text("Cancel Note")

    total_invoice = fields.Float(compute='_compute_sales_count',string='Invoices')
    is_package_claim = fields.Boolean(string='Is Claimed from Package', default=False)

    def _compute_sales_count(self):
        self.total_invoice = 0
        invoices = self.env['account.move'].search([('appointment_id', '=', self.id)])
        return True

    # function used to update customer's acquired pacakages..list will be shown once its paid already.. and ready for use..
    @api.onchange('partner_id','therapist_id','du_service_categ_id','appointments_type_id')
    def _onchange_update_partner_historys(self):
        if self.partner_id:
            appointment_ids = self.env['appointment.line.id'].search([
                ('appointment_id.partner_id','=',self.partner_id.id),
                ('therapist_id','=',self.therapist_id.id),
                ('service_categ_id','=',self.du_service_categ_id.id),
                ('appointments_type_id','=',self.appointments_type_id.id),
                ('state_line','=','draft'),('appointment_id.session_type','=','type_package'),
                ('appointment_id.payment_status_apt','=','payment_received')])

            line_vals = []
            for res in appointment_ids:
                # res.appointment_package_reference_id = self.id
                line_vals.append(res.id)
            self.apt_partner_historys = [(6, 0, line_vals)]

    #action for pacakege claim.. this will update payment dtate and necessory fields
    def action_pack_confirm(self):
        for res in self.apt_partner_historys:
            if res.state_line == 'confirm':

                self.write({'package_line_id':res.id,'parent_id':res.appointment_id.id})
                self.package_line_id.write({'time_id': False})
                self.package_line_id.write({'apt_room_id': self.apt_room_id,
                                            'booking_start_date': self.booking_date,
                                            'time_id': self.time_id.id,
                                            'time_slot_id': self.time_slot_id.id,
                                            'duration': self.duration,
                                            'start_time_str': self.start_time_str,
                                            'end_time_str': self.end_time_str,
                                            'start_time': self.start_time,
                                            'end_time': self.end_time,
                                            })

                self.package_line_id.confirm_package()


class CustomAppointmentsLine(models.Model):
    _inherit = 'appointment.line.id'

    service_confirmed_date = fields.Datetime(string='Confirmed Date & Time', copy=False)
    is_void = fields.Boolean(string='Apply Void', default=False)
    void_date = fields.Date(string="Void Date")
    appointment_package_reference_id = fields.Many2one('appointment.appointment')
    claimed_apt_date = fields.Date(related='appointment_package_reference_id.booking_date')
    claimed_apt_time_slot_id = fields.Many2one('time.slot',related='appointment_package_reference_id.time_slot_id')
    #modify the state of package line on claimed.. once done which needs to be confirmed for further update
    def action_claim_pack(self):
        if 'claim_operation' in self._context and self._context['claim_operation'] == True:
            # Made changes and pass the addional fields 01-07-22
            return {
                    'type': 'ir.actions.act_window',
                    'name': 'Appointment',
                    'view_mode': 'form',
                    'res_model': 'appointment.appointment',
                    'target': 'new',
                    'context': {
                                'default_partner_id': int(self._context.get('partner_id')) or self.appointment_id.partner_id.id,
                                'default_show_history': False,
                                'default_session_type': 'type_single',
                                'default_therapist_id': self.appointment_id.therapist_id.id,
                                'default_du_service_categ_id': self.service_categ_id.id,
                                'default_service_categ_id': self.service_categ_id.id,
                                'default_appointments_type_id': self.appointments_type_id.id,
                                'except_false': True,
                                'default_package_line_id': self.id,
                                'default_is_package_claim': True,
                                'default_partner_inv':True,
                                'default_time_id':self.appointment_id.time_id.id,
                                'default_time_slot_id':self.appointment_id.time_slot_id.id,
                                'default_apt_room_id':self.appointment_id.apt_room_id.id,
                                'default_apt_package_parent_id': self.appointment_id.id,
                    },
                }
        elif 'claim_operation' in self._context and self._context['claim_operation'] == False:
            self.state_line = 'confirm'
            self.single_session_id = self.appointment_id.id
            if 'apt_id' in self._context: 
                apt_id = self.env['appointment.appointment'].browse(int(self._context['apt_id']))
                apt_id.is_package_claim = True
                apt_id.apt_package_parent_id = self.appointment_id.id
                self.appointment_package_reference_id = apt_id.id
                apt_id.pos_order_id = self.appointment_id.pos_order_id.id
                count = 0
                for rec in self.appointment_id.appointment_line_id:
                    if rec.state_line in ['draft']:
                        count += 1
                count =  len(self.appointment_id.appointment_line_id) - count
                apt_id.sequence += '-' + str(count)
                

    # Void action in lines of package
    def action_void_line(self):
        rec = self.env['appointment.line.id'].search(
            [('state_line', '=', 'confirm'), ('appointment_id', '=', self.appointment_id.id)])
        if len(rec)>0 and not self.appointment_id.state == 'new':
            raise UserError(_("Not allowed to Void this Service. Some of the services are Availed Already..!!"))
        elif len(rec)==0 and self.appointment_id.state == 'new':
            raise UserError(_("Not allowed to Void this Service. Package is not Confirmed Yet..!!"))
        elif self.appointment_id.state in ('confirm','ongoing'):
            self.write({'state_line': 'void', 'is_void': True, 'void_date': datetime.now()})
            self.appointment_id.write({'state': 'ongoing'})
            if self.avail_id:
                self.avail_id.unlink()
        else:
            print()
        return True


class AccountInvAppts(models.Model):
    _inherit = 'account.move'

    apt_order_id = fields.Many2one('sale.order', string="Sale order")
