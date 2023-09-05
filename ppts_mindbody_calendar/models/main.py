# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)


class FavouriteCalendar(models.Model):
    _inherit = 'appointment.appointment'
   

    isfavourite = fields.Boolean(
       string='Favourite Therapist',
   )
   

   
