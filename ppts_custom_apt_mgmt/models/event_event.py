from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import time

class EventEvent(models.Model):
    _inherit = 'event.event'

    event_sub_categ_id = fields.Many2one('calendar.appointment.type','Sub Category',copy=False,tracking=True,help='Event Sub Category')
    event_service_categ_id = fields.Many2one('appointment.category', string="Services Category")
    image = fields.Binary(string="Image")
   

    @api.onchange('event_service_categ_id')
    def _compute_event_service(self):
        for each_event in self:
            if each_event.event_service_categ_id:
                each_event.event_type_id = each_event.event_service_categ_id.event_categ_id.id
            else:
                each_event.event_type_id = False

    @api.onchange('class_type')
    def _compute_from_event_type(self):
        for evnt in self:
            if evnt.class_type:
                if not evnt.name:
                    evnt.name = evnt.class_type.class_name
                if not evnt.evnt_maincateg:
                    evnt.evnt_maincateg = evnt.class_type.class_main_catg
                if not evnt.evnt_subcateg:
                    evnt.evnt_subcateg = evnt.class_type.class_sub_catg
                if not evnt.event_sub_categ_id:
                    evnt.event_sub_categ_id = evnt.class_type.event_sub_categ_id   
                if not evnt.event_img_url:
                    evnt.event_img_url = evnt.class_type.class_image_url
                if not evnt.event_img:
                    evnt.event_img = evnt.class_type.class_image
                # if not evnt.event_desc:
                #     evnt.event_desc = evnt.class_type.class_name
                if not evnt.description:
                    evnt.description = evnt.class_type.class_description
                if not evnt.type_event:
                    evnt.type_event = evnt.class_type.type_event
                if not evnt.type_online:
                    evnt.type_online = evnt.class_type.type_online
                if not evnt.address_id:
                    evnt.address_id = evnt.class_type.address_id
                if not evnt.event_survey_id:
                    evnt.event_survey_id = evnt.class_type.event_survey_id

                if not evnt.class_level_id:
                    evnt.class_level_id = evnt.class_type.class_level

                if not evnt.event_type_id:
                    evnt.event_type_id = evnt.class_type.eve_class_type


class CustomClassMST(models.Model):
    _inherit = 'event.class.master'

    event_sub_categ_id = fields.Many2one('calendar.appointment.type','Sub Category',copy=False,tracking=True,help='Event Sub Category')