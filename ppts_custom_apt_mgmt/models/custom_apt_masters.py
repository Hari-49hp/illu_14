from odoo import api, fields, models, _

class ApointmentMainCateg(models.Model):
    _name = 'appointment.category'
    _order = "sequence,id"
    _description = 'Appointment Service Category'
    _rec_name = 'name'

    def _default_sequence(self):
        """Sort new records at the end of the list."""
        sequence = 0
        for record in self.search([]):
            sequence = max(sequence, record.sequence + 1)
            return sequence

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence',default=_default_sequence)
    maincateg_code = fields.Char('Code')
    maincateg_notes = fields.Text('Internal Note')
    active_id = fields.Boolean('Active')
    is_event_sub_category = fields.Boolean('Event SubCategory',help="Is Event SubCateg")
    event_categ_id = fields.Many2one('event.type',string='Event Category')
    feature_in_homepage = fields.Boolean(string='Feature', help='Feature in Homepage')
    image = fields.Binary('Image', attachment=True)
    website_publish = fields.Boolean(string='Publish', help='Website Publish')
    tag_ids = fields.Many2many('tag.by.therapy', string='Tags')
    is_training = fields.Boolean(string='Is Traning', help='Is Traning')
    is_corporate = fields.Boolean(string='Is Corporate', help='Is Corporate')
    is_retreats = fields.Boolean(string='Is Retreats', help='Is Retreats')
    is_meditation = fields.Boolean(string='Is Meditation', help='Is Meditation')
    category_type = fields.Selection([('therapy','Therapy'),('healing','Healing')],string='Type')
    color_code = fields.Char('Calendar Card Color')
    is_event = fields.Boolean(string="Is Event")
    is_appointment = fields.Boolean(string="Is Appointment")

    @api.model
    def create(self, vals):
        program = super(ApointmentMainCateg, self).create(vals)

        pr_categ_id = self.env['product.category'].search([('name', '=', 'Appointment')], limit=1)

        if not pr_categ_id:
            pr_categ = self.env['product.category'].create({
                'name': 'Appointment',
            })

        pr_categ = self.env['product.category'].create({
            'name': program.name,
            'parent_id': pr_categ_id.id,
        })
        return program

class AppointmentCancelReason(models.Model):
    _name = 'appointment.cancel.reason'
    _description = 'Appointment Cancel Reason'
    _rec_name = 'name'

    name = fields.Char('Reason')

class ApointmenttypeCateg(models.Model):
    _name = 'appointment.type.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment Type Category'
    _rec_name = 'name'

    name = fields.Char('Name')
    maincateg_code = fields.Char('Code')
    maincateg_notes = fields.Text('Internal Note')


class ApointmentSubCateg(models.Model):
    _name = 'appointment.sub.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment Sub Category'
    _rec_name = 'name'

    name = fields.Char('Sub Category Name',translate=False)
    sarvice_categ_id = fields.Many2one('appointment.category', string='Service Category')
    sarvice_categ_code = fields.Char('Service Category Code', related='sarvice_categ_id.maincateg_code')
    tag_by_therapy_id = fields.Many2many('tag.by.therapy', 'appointment_sub_category_tag_by_therapy_id', string='Tag By Therapy')
    code = fields.Char('Sub Category Code')
    notes = fields.Text('Internal Note')
    main_categ_id = fields.Many2one('appointment.type.category', string='Appointment Category', copy=False)


    @api.model
    def create(self, vals):
        res = super(ApointmentSubCateg, self).create(vals)

        for i in res.tag_by_therapy_id:
            i.write({
                'service_categ_ids': [(4, res.sarvice_categ_id.id)],
                'service_sub_categ_ids': [(4, res.id)]
                })

        return res

    def write(self, vals):
        res = super(ApointmentSubCateg, self).write(vals)

        for i in self.tag_by_therapy_id:
            i.write({
                'service_categ_ids': [(4, self.sarvice_categ_id.id)],
                'service_sub_categ_ids': [(4, self.id)]
                })

        return res




class ApointmentSourceCateg(models.Model):
    _name = 'appointment.source'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment Source'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
    notes = fields.Text('Internal Note')

class ApointmentEmailReminder(models.Model):
    _name = 'appointment.remainder'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Appointment Remainder'

    user_id = fields.Many2one('res.users', string='User')
    email = fields.Char('Email', related='user_id.login')

class ApointmentQuickRemark(models.Model):
    _name = 'appointment.quick.remark'
    _description = 'Appointment Quick Remarks'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')
