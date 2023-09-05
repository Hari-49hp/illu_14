from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import re
class EventEventTicket(models.Model):
    _inherit = 'event.event.ticket'

    def name_get(self):
        rec_name = []
        for rec in self:
            name = rec.name +' '+ '[' + rec.ticket_type + ']'
            rec_name.append((rec.id, name))
        return rec_name

    ticket_type = fields.Selection([('online','Online'),
                                    ('offline','Manual'),
                                    ('waiting','Waiting List')],
                                   'Ticket Type',default='online',help='Type of Ticket.',required=True)

    full_price = fields.Integer(string="Full Price",help='Price of Ticket without Discount.')
    discount_type = fields.Selection([
        ('type_nodisc', 'No Discount'),
        ('type_percentage', 'Percentage')],default='type_nodisc',
        required=True,
        string="Disc. Type",help='Type of Discount to be Applied for ticket.')
    disc_rate = fields.Integer(string="Discount",help='Value of Discount to Be Applied, either Percentage or Fixed Rate.')

    @api.onchange('price','discount_type','disc_rate')
    def get_full_price(self):
        for rec in self:
            if rec.price:
                # if rec.discount_type == 'type_flat':
                #     rec.full_price = rec.price - rec.disc_rate
                if rec.discount_type=='type_percentage':
                    d_price=(rec.price * rec.disc_rate)/100
                    rec.full_price = rec.price - d_price
                else:
                    rec.full_price = rec.price

class Event(models.Model):
    _inherit = 'event.event'

    @api.model
    def create(self, vals):
        res = super(Event, self).create(vals)
        product_id = self.env['product.product'].search([('default_code', '=', 'EVENT_REG')], limit=1)
        project_stage_id = self.env['project.task.type'].search([('sequence','=',0)],limit=1)
        class_checklist = res.class_type.class_checklist_line_ids
        if class_checklist:
            create_checklist_id = self.env['check.list'].create({
                'event_id': res.id,
            })
            for lst_ids in class_checklist:
                create_line_id = self.env['check.list.line'].create({
                    'checklist_master_id': lst_ids.checklist_master_id.id,
                    'checklist_description': lst_ids.checklist_description,
                    'checklist_category_id': lst_ids.checklist_category_id.id,
                    'checklist_responsible': lst_ids.checklist_responsible.id,
                    'check_list_id': create_checklist_id.id,
                    'start_date': res.date_begin,
                    'end_date': res.date_end,
                    'status': project_stage_id.id
                })
        class_room_id = res.class_type.class_room_id
        if not res.survey_id:
            class_survey_id = res.event_survey_id
            if class_survey_id:
                new_id = class_survey_id.copy()
                event_name = class_survey_id.title
                new_id.write({'title': event_name,
                              'event_id': res.id,
                              'event_active': True,
                              'is_template': False,
                              'state': 'draft'})
                res.survey_id = new_id.id
        note_id = self.env['event.notification'].search([], limit=1)
        ctx = dict()
        if note_id.event_active_notification_create == True:
            for i in note_id.event_create_mailing_list:
                for il in self.env['mailing.contact'].sudo().search([]):
                    if il.email and i.id in il.subscription_list_ids.ids:
                        for j in i.event_create_mail:
                            ctx.update({
                                'name': res.name,
                                'email': il.email,
                                'customer_name': il.name,
                            })
                            j.sudo().with_context(ctx).send_mail(il.id, force_send=True)
                    if il.mobile and i.id in il.subscription_list_ids.ids and i.event_create_whatsapp:
                        res.whatsapp_sent(partner_id=il.id, tmpl_id=i.event_create_whatsapp.id, pt='mailing_list')
        return res

    def write(self, vals):
        res = super(Event, self).write(vals)
        for each in self:
            if each.event_meeting_room_id:
                query = "update event_meeting_room set room_id = " + str(each.room_id.id) + " " + "where id = " + str(
                    each.event_meeting_room_id.id)
                self.env.cr.execute(query)
        return res