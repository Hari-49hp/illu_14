from odoo import api, fields, models, _
from datetime import date, timedelta, datetime

TIME = [('08:00','08:00'),('08:15','08:15'),('08:30','08:30'),('08:45','08:45'),('09:00','09:00'),('09:15','09:15'),('09:30','09:30'),('09:45','09:45'),('10:00','10:00'),('10:15','10:15'),('10:30','10:30'),('10:45','10:45'),('11:00','11:00'),('11:15','11:15'),('11:30','11:30'),('11:45','11:45'),('12:00','12:00'),('12:15','12:15'),('12:30','12:30'),('12:45','12:45'),('13:00','13:00'),('13:15','13:15'),('13:30','13:30'),('13:45','13:45'),('14:00','14:00'),('14:15','14:15'),('14:30','14:30'),('14:45','14:45'),('15:00','15:00'),('15:15','15:15'),('15:30','15:30'),('15:45','15:45'),('16:00','16:00'),('16:15','16:15'),('16:30','16:30'),('16:45','16:45'),('17:00','17:00'),('17:15','17:15'),('17:30','17:30'),('17:45','17:45'),('18:00','18:00'),('18:15','18:15'),('18:30','18:30'),('18:45','18:45'),('19:00','19:00'),('19:15','19:15'),('19:30','19:30'),('19:45','19:45'),('20:00','20:00'),('20:15','20:15'),('20:30','20:30'),('20:45','20:45'),('21:00','21:00'),('21:15','21:15'),('21:30','21:30'),('21:45','21:45'),('22:00','22:00'),('22:15','22:15'),('22:30','22:30'),('22:45','22:45'),('23:00','23:00'),('23:15','23:15'),('23:30','23:30'),('23:45','23:45')]

class Time(models.Model):
    _name = 'time.time'
    _description = 'Time'
    _order = 'duration asc'

    name = fields.Char('Name', required=True)
    duration = fields.Integer('Duration', required=True)

    def slot_time(self):
        def get_daily_slots(start, end, slot, date):
            dt = datetime.combine(date, datetime.strptime(start,"%H:%M").time())
            slots = [dt.time().strftime("%H:%M:%S")[:-3]]
            while (dt.time() < datetime.strptime(end,"%H:%M").time()):
                dt = dt + timedelta(minutes=slot)
                slots.append(dt.time().strftime("%H:%M:%S")[:-3])
                if dt < datetime.now() + timedelta(days = 1):
                    break
            return slots
        lst = [];line_ids = []

        start_time = ['08:00','08:15','08:30','08:45','09:00','09:15','09:30','09:45','10:00','10:15','10:30','10:45','11:00','11:15','11:30','11:45','12:00','12:15','12:30','12:45','13:00','13:15','13:30','13:45','14:00','14:15','14:30','14:45','15:00','15:15','15:30','15:45','16:00','16:15','16:30','16:45','17:00','17:15','17:30','17:45','18:00','18:15','18:30','18:45','19:00','19:15','19:30','19:45','20:00','20:15','20:30','20:45','21:00','21:15','21:30','21:45','22:00','22:15','22:30','22:45','23:00','23:15','23:30']
        end_time = '23:45'
        for dd in start_time:
            slot_time = self.duration
            days = 1
            for j in range(days):
                date_required = datetime.now().date() + timedelta(days=0)
            time_slot = get_daily_slots(start=dd, end=end_time, slot=slot_time, date=date_required)
            for i in range(len(time_slot)):
                lst.append((time_slot*2)[i:i+2])
            lst.pop()
            for o in lst:
                TIMESLOT = self.env['time.slot']
                if o[1] == '00:00': break
                # if o[1] == '19:15': break
                # if o[1] == '20:15': break
                # if o[1] == '23:00': break
                # if o[1] == '23:30': break
                # if o[1] == '23:45': break
                slot_id = TIMESLOT.search([('start_time','=',o[0]),('end_time','=',o[1])])
                if not slot_id:
                    TIMESLOT.create({
                        'name': str(o[0] +'-'+o[1]),
                        'start_time': o[0],
                        'end_time': o[1],
                        })

    def view_slot(self):
        return {
                'type': 'ir.actions.act_window',
                'name': _('Time Slot'),
                'res_model': 'time.slot',
                'target': 'new',
                'view_mode': 'tree',
                'view_type': 'tree',
                }

class Time(models.Model):
    _name = 'time.slot'
    _description = 'Time Slot'
    _order = 'start_time asc'

    name = fields.Char('Name')
    start_time = fields.Selection(TIME, string='Start Time')
    end_time = fields.Selection(TIME, string='End Time')


class DurationPrice(models.Model):
    _name = 'duration.price'
    _description = 'Duration Price'

    time_id = fields.Many2one('time.time', string='Duration')
    price = fields.Float('Price')
    apt_type_id = fields.Many2one('calendar.appointment.type', string='Apt Type')

class DateDate(models.Model):
    _name = 'date.date'
    _description = 'Date'

    name = fields.Char('Date')
    date = fields.Date('Date')