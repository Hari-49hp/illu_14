from odoo import api, fields, models, _
import json, werkzeug

class ApointmentMainCateg(models.Model):
    _inherit = 'appointment.category'

    is_struggling = fields.Boolean(string='Is Struggling', help='Is Struggling')


    def corporate_service_5section(self):
        # service_categ_id = self.env['appointment.category'].sudo().search([('is_corporate','=',True),('website_publish','=',True)],limit=1)
        # payrate_ids = self.env['hr.employee.payrate'].sudo().search([('service_category_type_id','=',service_categ_id.id)])

        class_list = ['corwell_one','corwell_two','corwell_three','corwell_four','corwell_five']; content = []; employee = []
        employee = []
        corporate_employee = self.env['hr.employee'].search([('corporate_employees','=',True)])

        for j in corporate_employee:
            employee.append(j.id)
        employee = list(dict.fromkeys(employee))
        count = 0
        content = []
        for i in employee[:5]:
            i = self.env['hr.employee'].sudo().browse(i)
            content.append({
                'class': class_list[count],
                'name': i.name,
                # 'job': i.get_job_position_website(),
                'job':i.get_by_support_website(),
               'location': i.company_id.name,
                'employee_id': i.id,
                'img': '/web/image?model=hr.employee&id=%s&field=image_1920' % (i.id) if i.image_1920 else '/ppts_website_theme/static/src/img/expert1.jpg',
            })
            count+=1
        return content
        # return json.dumps(content)
