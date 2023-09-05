from odoo import api, fields, models, _

class MasterAboutus(models.Model):
    _name = 'master.aboutus'
    _description = 'About Us'
    
    name = fields.Char('How Did You Hear About Us?',required=True)
    sequence = fields.Char('Sequence',required=True)
    sequence_first = fields.Char('Sequence First Name',default='ILLU')
    
class MasterIntrestedin(models.Model):
    _name = 'master.intrestedin'
    _description = 'Intrested In'
    
    name = fields.Char('What Services Are you Interested In?',required=True)
    
class MasterStruggling(models.Model):
    _name = 'master.struggling'
    _description = 'Struggling'
    
    name = fields.Char('Which Areas are you struggling with?',required=True)
    
class Masterholistic(models.Model):
    _name = 'master.holistic'
    _description = 'Holistic'
    
    name = fields.Char('Which Holistic Approaches are you interested in?',required=True)
    
class Mastermembership(models.Model):
    _name = 'master.membership'
    _description = 'Membership'
    
    name = fields.Char('Membership Status?',required=True)
    
class MasterBranch(models.Model):
    _name = 'master.branch'
    _description = 'Branch'
    
    sequence_first = fields.Char('Sequence First Name',default='Ilu')
    name = fields.Char('Branch Name',required=True)
    sequence = fields.Char('Sequence',required=True)
    street = fields.Char('Street1')
    street1 = fields.Char('Street2')
    country_id = fields.Many2one('res.country',string="Country")
    state_id = fields.Many2one('res.country.state',string="State")
    city = fields.Char('City')
    zip = fields.Char('Zip')

class MasterOnline(models.Model):
    _name = 'master.online'
    _description = 'Online'

    name = fields.Char('Where did you find out about us?',required=True)

class MasterRefferal(models.Model):
    _name = 'master.refferal'
    _description = 'Refferal'

    name = fields.Char('Referral Type',required=True)

class MasterCustomer(models.Model):
    _name = 'master.customer'
    _description = 'Customer'
    _inherit = ['mail.thread']

    partner_id = fields.Many2one('res.partner', 'Customer Name',required=True)
    date_first_visit = fields.Date('Date of First Visit',required=True)
    date_last_visit = fields.Date('Date of Last Visit',required=True)
    total_number_visit = fields.Char('Total Number Visits',required=True)
    average_visit_month = fields.Char('Average Visits Per Month',required=True)
    average_service_utilize = fields.Char('Average Service Utilization Per Visit',required=True)
        
class MasterVisit(models.Model):
    _name = 'master.visit'
    _description = 'Visit'

    name = fields.Char('Visit',required=True)

class MasterCategory(models.Model):
    _name = 'master.category'
    _description = 'Category'

    name = fields.Char('Category',required=True)

class CityMaster(models.Model):
    _name = 'city.master'
    _description = 'City'

    name = fields.Char('Name')
    state_id = fields.Many2one('res.country.state',string='State' , domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country',string='Country ')

