from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError




class EmployeeQualifiedIn(models.Model):
    _name = 'employee.qualified.in'
    _description ="EmployeeQualifiedIn"

    name = fields.Char(string='Name')
    code = fields.Char(string="Code")

class EmployeeHelp(models.Model):
    _name = 'employee.help'
    _description ="EmployeeHelp"

    name = fields.Char(string='Name')
    code = fields.Char(string="Code")

class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    by_platform = fields.Selection([('online','Online'),('onsite','Onsite'),('online/onsite','Online/Onsite')],string='By Platform')
    corporate_employees = fields.Boolean(string="Corporate Employee",help="Based on the selection the employee will be listed in the website under the corporate menu")
    by_support = fields.Many2many('by.support',string='By Support')
    by_solution = fields.Many2many('by.solution',string='By Solution')
    feature_in_homepage = fields.Boolean(string='Feature', help='Feature in Homepage')
    feature_in_wellness = fields.Boolean(string='Wellness Speaker', help='Feature in Wellness retreat Speaker')

    about_employee = fields.Html("About Employee",help='Display in Website Employee About')
    about_employee_in_paragraph =fields.Html("Paragraph",help='Display in Website Employee About')
    video_about_url = fields.Char("Video About URL",help='Display in Website Employee About Video URL')
    video_about_employee = fields.Html("Video About",help='Display in Website Employee About Video')
    video_about_employee_in_paragraph =fields.Html("Video Paragraph",help='Display in Website Employee About Video')
    partner_id = fields.Many2one('res.partner',string="Related Client",help="Employee will be created as partner",readonly=True)
    employee_qualification_lines = fields.One2many('employee.qualifications', 'employee_id', string="Employee Qualifications'")
    image_attachment_ids = fields.Many2many('ir.attachment', string='Image Attachments')
    qualified_id = fields.Many2one('employee.qualified.in','Qualified In')
    help_id = fields.Many2one('employee.help','To Help me with')

    # Raise warning if select corporate employee more than 5
    @api.constrains('corporate_employees')
    def action_corporate_employees(self):
        get_corporate_emp = self.search([('corporate_employees','=',True)])
        if len(get_corporate_emp) > 5:
            raise ValidationError(_('This list already exceeds the number of corporate employees, so if you want to add new employees, you must disable the previous list.'))


    def youtube_embed(self):
        embedUrl = False
        if self.video_about_url:
            import re
            videoUrl = self.video_about_url
            embedUrl = re.sub(r"(?ism).*?=(.*?)$", r"https://www.youtube.com/embed/\1?modestbranding=1", videoUrl )
            return embedUrl
        else: return embedUrl

    @api.model
    def create(self, vals):
        res = super(HrEmployeeBase, self).create(vals)
        value = {
        'name': res.name or "",
        'mobile':res.work_phone,
        'email':res.work_email,
        'customer_rank':0,
        'company_type':'company',
        'alternate_mobile':False,
        'alternate_email':False,
        'type':'contact',
        'is_employee':True,
        'hr_id':res.id,
        }
        partner_id = self.env['res.partner'].create(value)
        res.partner_id = partner_id.id
        return res 


    def action_user_creation(self):
        name = self.name.split(" ", 1)
        first_name = name[0]
        last_name = name[1]
        views = [(self.env.ref('base.view_users_form').id, 'form')]

        ctx = {
            'default_firstname':first_name,
            'default_lastname':last_name,
            'default_name':self.name,
            'default_work_email':self.work_email or "",
            'default_login':self.work_email or "",
            'employee_vals':self.id,
            'default_employee_id':self.id,
            'default_hr_id':self.id
        }

        return {
            'type': 'ir.actions.act_window',
            'name': 'User',
            'view_mode': 'form',
            'views':views,
            'res_model': 'res.users',
            'target': 'new',
            'context':ctx,
            
        }

class EmployeeQualifications(models.Model):
    _name = 'employee.qualifications'
    _description ="EmployeeQualifications"

    name = fields.Char(string='name')
    employee_id = fields.Many2one("hr.employee",string="Hr Employee")


class Resusers(models.Model):
    _inherit='res.users'
    

    employee_vals = fields.Char("Employee Value")


    @api.model
    def create(self, vals):
        value = self.env.context.get('employee_vals')
        res = super(Resusers, self).create(vals)
        if value:
            hr_id = self.env['hr.employee'].browse(value)
            hr_id.user_id = res.id
        return res