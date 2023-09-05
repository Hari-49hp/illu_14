from odoo import api, fields, models, _
from datetime import datetime


class CallFeedback(models.TransientModel):
    _name = 'call.feedback'
    _description = 'Call Feedback'

    
    remarks = fields.Text(string="Call Remarks")
    current_model = fields.Char(string="Model")
    current_id = fields.Char(string="ID")
    customer_name = fields.Char(compute='_compute_get_customer')
    remark_id = fields.Many2one('appointment.quick.remark',string="Quick Remarks")
    time = fields.Char(string="Timer",default="00:00:00")

    @api.depends('current_model','current_id')
    def _compute_get_customer(self):
        current_record = self.env[self.current_model].browse(int(self.current_id))
        if self.current_id and self.current_model == 'crm.lead':
            self.customer_name = current_record.partner_id.name
        if self.current_id and self.current_model == 'res.partner':
            get_partner_id = self.env['res.partner'].search([('id','=',current_record.id)])
            if get_partner_id:
                self.customer_name = get_partner_id.name


    # create the record based on remarks in crm.lead(Not Available) 15-09-22
    def action_not_available(self):
        get_current_record = self.env[self.current_model].browse(int(self.current_id))
        if self.current_model == 'crm.lead':
            self.env['call.history'].create({
                'remarks':self.remarks,
                'call_date':datetime.today(),
                'user_id':self.env.user.id,
                'quick_remark':'Not Available/Try Again Later',
                'call_history_id':get_current_record.id
                })
            # also create the record in partner while call in the crm based on remarks 15-09-22
            if get_current_record.partner_id:
                get_partner_id = self.env['res.partner'].search([('id','=',get_current_record.partner_id.id)])
                if get_partner_id:
                    self.env['partner.call.history'].create({
                    'partner_call_id':get_partner_id.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'Not Available/Try Again Later',
                    })
                    # create the log in res.partner based on remarks creation 16-09-22
                    msg_body = """Quick Remarks : """ + str('Not Available/Try Again Later' or 'N/A') + """ <br/> """+\
                                """Notes : """ + str(self.remarks) + """ <br/> """+\
                                """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                                """Date : """ + str(datetime.today()) + """ <br/> """
                                
                                           
                    get_partner_id.message_post(body=msg_body)
                    # refresh the current page using below code 16-09-22
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
        if self.current_model =='res.partner':
            # create the record based on remarks in res.partner 15-09-22
            partner_id = self.env['partner.call.history'].create({
                    'partner_call_id':get_current_record.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'Not Available/Try Again Later',
                    
                })
            # create the log in res.partner based on remarks creation 16-09-22
            msg_body = """Quick Remarks : """ + str('Not Available/Try Again Later' or 'N/A') + """ <br/> """+\
                        """Notes : """ + str(self.remarks) + """ <br/> """+\
                        """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                        """Date : """ + str(datetime.today()) + """ <br/> """
            partner_id.partner_call_id.message_post(body=msg_body)
            # refresh the current page using below code 16-09-22
            return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }


# create the record based on remarks in crm.lead(No Answer) 16-09-22
    def action_no_answer(self):
        get_current_record = self.env[self.current_model].browse(int(self.current_id))
        if self.current_model == 'crm.lead':
            self.env['call.history'].create({
                'remarks':self.remarks,
                'call_date':datetime.today(),
                'user_id':self.env.user.id,
                'quick_remark':'No Answer',
                'call_history_id':get_current_record.id
                })
            # also create the record in partner while call in the crm based on remarks 15-09-22
            if get_current_record.partner_id:
                get_partner_id = self.env['res.partner'].search([('id','=',get_current_record.partner_id.id)])
                if get_partner_id:
                    self.env['partner.call.history'].create({
                    'partner_call_id':get_partner_id.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'No Answer',
                    })
                    # create the log in res.partner based on remarks creation 16-09-22
                    msg_body = """Quick Remarks : """ + str('No Answer' or 'N/A') + """ <br/> """+\
                                """Notes : """ + str(self.remarks) + """ <br/> """+\
                                """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                                """Date : """ + str(datetime.today()) + """ <br/> """
                                
                                           
                    get_partner_id.message_post(body=msg_body)
                    # refresh the current page using below code 16-09-22
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
        if self.current_model =='res.partner':
            # create the record based on remarks in res.partner 15-09-22
            partner_id = self.env['partner.call.history'].create({
                    'partner_call_id':get_current_record.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'No Answer',
                    
                })
            # create the log in res.partner based on remarks creation 16-09-22
            msg_body = """Quick Remarks : """ + str('No Answer' or 'N/A') + """ <br/> """+\
                        """Notes : """ + str(self.remarks) + """ <br/> """+\
                        """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                        """Date : """ + str(datetime.today()) + """ <br/> """
            partner_id.partner_call_id.message_post(body=msg_body)
            # refresh the current page using below code 16-09-22
            return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
    # callback
    def action_callback(self):
        get_current_record = self.env[self.current_model].browse(int(self.current_id))
        if self.current_model == 'crm.lead':
            self.env['call.history'].create({
                'remarks':self.remarks,
                'call_date':datetime.today(),
                'user_id':self.env.user.id,
                'quick_remark':'Callback',
                'call_history_id':get_current_record.id
                })
            # also create the record in partner while call in the crm based on remarks 15-09-22
            if get_current_record.partner_id:
                get_partner_id = self.env['res.partner'].search([('id','=',get_current_record.partner_id.id)])
                if get_partner_id:
                    self.env['partner.call.history'].create({
                    'partner_call_id':get_partner_id.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'Callback',
                    })
                    # create the log in res.partner based on remarks creation 16-09-22
                    msg_body = """Quick Remarks : """ + str('Callback' or 'N/A') + """ <br/> """+\
                                """Notes : """ + str(self.remarks) + """ <br/> """+\
                                """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                                """Date : """ + str(datetime.today()) + """ <br/> """
                                
                                           
                    get_partner_id.message_post(body=msg_body)
                    # refresh the current page using below code 16-09-22
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
        if self.current_model =='res.partner':
            # create the record based on remarks in res.partner 15-09-22
            partner_id = self.env['partner.call.history'].create({
                    'partner_call_id':get_current_record.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'Callback',
                    
                })
            # create the log in res.partner based on remarks creation 16-09-22
            msg_body = """Quick Remarks : """ + str('Callback' or 'N/A') + """ <br/> """+\
                        """Notes : """ + str(self.remarks) + """ <br/> """+\
                        """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                        """Date : """ + str(datetime.today()) + """ <br/> """
            partner_id.partner_call_id.message_post(body=msg_body)
            # refresh the current page using below code 16-09-22
            return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
    # followup 
    def action_followup(self):
        get_current_record = self.env[self.current_model].browse(int(self.current_id))
        if self.current_model == 'crm.lead':
            self.env['call.history'].create({
                'remarks':self.remarks,
                'call_date':datetime.today(),
                'user_id':self.env.user.id,
                'quick_remark':'For Follow-up',
                'call_history_id':get_current_record.id
                })
            # also create the record in partner while call in the crm based on remarks 15-09-22
            if get_current_record.partner_id:
                get_partner_id = self.env['res.partner'].search([('id','=',get_current_record.partner_id.id)])
                if get_partner_id:
                    self.env['partner.call.history'].create({
                    'partner_call_id':get_partner_id.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'For Follow-up',
                    })
                    # create the log in res.partner based on remarks creation 16-09-22
                    msg_body = """Quick Remarks : """ + str('For Follow-up' or 'N/A') + """ <br/> """+\
                                """Notes : """ + str(self.remarks) + """ <br/> """+\
                                """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                                """Date : """ + str(datetime.today()) + """ <br/> """
                                
                                           
                    get_partner_id.message_post(body=msg_body)
                    # refresh the current page using below code 16-09-22
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
        if self.current_model =='res.partner':
            # create the record based on remarks in res.partner 15-09-22
            partner_id = self.env['partner.call.history'].create({
                    'partner_call_id':get_current_record.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'For Follow-up',
                    
                })
            # create the log in res.partner based on remarks creation 16-09-22
            msg_body = """Quick Remarks : """ + str('For Follow-up' or 'N/A') + """ <br/> """+\
                        """Notes : """ + str(self.remarks) + """ <br/> """+\
                        """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                        """Date : """ + str(datetime.today()) + """ <br/> """
            partner_id.partner_call_id.message_post(body=msg_body)
            # refresh the current page using below code 16-09-22
            return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
    # DNC  
    def action_dnc(self):
        get_current_record = self.env[self.current_model].browse(int(self.current_id))
        if self.current_model == 'crm.lead':
            self.env['call.history'].create({
                'remarks':self.remarks,
                'call_date':datetime.today(),
                'user_id':self.env.user.id,
                'quick_remark':'Do not call',
                'call_history_id':get_current_record.id
                })
            # also create the record in partner while call in the crm based on remarks 15-09-22
            if get_current_record.partner_id:
                get_partner_id = self.env['res.partner'].search([('id','=',get_current_record.partner_id.id)])
                if get_partner_id:
                    self.env['partner.call.history'].create({
                    'partner_call_id':get_partner_id.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'Do not call',
                    })
                    # create the log in res.partner based on remarks creation 16-09-22
                    msg_body = """Quick Remarks : """ + str('Do not call' or 'N/A') + """ <br/> """+\
                                """Notes : """ + str(self.remarks) + """ <br/> """+\
                                """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                                """Date : """ + str(datetime.today()) + """ <br/> """
                                
                                           
                    get_partner_id.message_post(body=msg_body)
                    
                    # refresh the current page using below code 16-09-22
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }
        if self.current_model =='res.partner':
            # create the record based on remarks in res.partner 15-09-22
            partner_id = self.env['partner.call.history'].create({
                    'partner_call_id':get_current_record.id,
                    'remarks':self.remarks,
                    'call_date':datetime.today(),
                    'user_id':self.env.user.id,
                    'quick_remark':'Do not call',
                    
                })
            # create the log in res.partner based on remarks creation 16-09-22
            msg_body = """Quick Remarks : """ + str('Do not call' or 'N/A') + """ <br/> """+\
                        """Notes : """ + str(self.remarks) + """ <br/> """+\
                        """User : """ + str(self.env.user.name or 'N/A') + """ <br/> """ +\
                        """Date : """ + str(datetime.today()) + """ <br/> """
            partner_id.partner_call_id.message_post(body=msg_body)
            # refresh the current page using below code 16-09-22
            return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                        }

   
