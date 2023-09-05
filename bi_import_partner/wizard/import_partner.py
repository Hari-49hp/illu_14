# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import io
import xlrd
import babel
import logging
import tempfile
import binascii
from io import StringIO,BytesIO
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
import datetime as dt


_logger = logging.getLogger(__name__)
import xlrd as xl

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportPartner(models.TransientModel):
    _name = 'import.partner'
    _description = 'Import Partner'

    file_type = fields.Selection([('CSV', 'CSV File'),('XLS', 'XLS File')],string='Upload a File', default='CSV')
    file = fields.Binary(string="Upload a File")
    merge_duplicate_cont = fields.Boolean(string="Merge Duplicate Contacts")
    success_message = fields.Boolean(string="Success",help="While true this check box it will open the success message")
    file_name = fields.Char(string="File Name")
    import_count = fields.Integer(string="Import Count")
    total_count = fields.Integer(string="Total Count")
    filename = fields.Char(string='File Name', size=64)
    excel_file = fields.Binary(string='Report File')

    def import_partner(self):
        self.success_message = True
        if not self.file:
            raise ValidationError(_("Please Upload File to Import Partner !"))

        if self.file_type == 'CSV':
            line = keys = ['name','first_name','last_name','email','mobile','is_a_customer']
            try:
                csv_data = base64.b64decode(self.file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))
                
            values = {}
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                    else:
                        res = self.create_partner(values)
                        # create_vals = self.action_merge_contact(values)
        else:
            try:
                file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                file.write(binascii.a2b_base64(self.file))
                file.seek(0)
                values = {}
                workbook = xlrd.open_workbook(file.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Please Select Valid File Format !"))

            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    values.update( {
                            # 'name':line[0],
                            # 'first_name': line[1],
                            # 'last_name': line[2],
                            # 'email':line[3],
                            # 'mobile':line[4].split('.')[0],
                            # 'country':line[5],
                            # 'state':line[6],
                            # 'city':line[7],
                            # 'gender':line[8],
                            # 'lead':line[9],
                            # 'is_a_customer':line[5],
                            'first_name': line[0],
                            'last_name': line[1],
                            'address':line[2],
                            'city':line[3],
                            'state':line[4],
                            'zip':line[5],
                            'date_of_birth':line[6],
                            'gender':line[7],
                            'location':line[8],
                            'mobile':line[9].split('.')[0],
                            'email':line[10],
                            'alternate_mobile':line[11].split('.')[0],
                            'alternate_email':line[12],
                            'lead':line[13],
                            })
                    res = self.create_partner(values)
        # To get the excel sheet count 02-08-22
        wb = xlrd.open_workbook(file.name)            #opening & reading the excel file
        s1 = wb.sheet_by_index(0)                     #extracting the worksheet
        s1.cell_value(0,0)                            #initializing cell from the excel file mentioned through the cell position
  
        # once excel report uploaded it will open the below page 02-08-22
        if self.success_message:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Success Message',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'success.message',
                'context': {
                'default_file': self.file_name,
                'default_import_count':self.import_count,
                'default_total_count':s1.nrows - 1,
                'default_skipped_count':(s1.nrows - 1) - self.import_count
            },
            }

    def create_partner(self, values):   
        partner = self.env['res.partner']
        # country_vals = self.get_country(values)
        state_vals = self.get_state(values)
        city_vals = self.get_city(values)
        reffer_type_vals = self.get_reffer(values)
        location_ids = self.action_get_location(values)
        get_dob = self.get_birth_date(values)
        # get campaign active id 02-08-22
        active_id = self._context.get('active_id')
        rec_campaign_id = self.env["asterisk_dialer.campaign"].browse(active_id)
        get_contact = self.env['asterisk_dialer.contact'].search([('phone','ilike',values.get('mobile').split('.')[0]),('campaign','=',rec_campaign_id.id)]) 
        # create the new contact based on the excel import 02-08-22
        get_customer = self.env['res.partner'].search([('mobile','=',values.get('mobile'))])
        partner_id = self.env['res.partner'].search([('mobile','=',values.get('mobile'))])
        # create the new customer if customer does not exist in the customer master 02-08-22
        res = ''
        if not partner_id:
            vals = {
                # 'name' : values.get('name'),
                # 'firstname' : values.get('first_name'),
                # 'lastname' : values.get('last_name'),
                # 'email' : values.get('email'),
                # 'mobile' : values.get('mobile').split('.')[0],
                # 'country_id':country_vals.id,
                # 'state_id':state_vals.id,
                # 'city_id':city_vals.id,
                # 'gender':values.get('gender'),
                # 'reffer_type_id':reffer_type_vals.id,
                # 'company_type':'person',
                # # 'is_a_customer':values.get('is_a_customer')
                # 'alternate_email':False
                'firstname' : values.get('first_name'),
                'lastname' : values.get('last_name'),
                'street':values.get('address'),
                'city_id': city_vals.id if city_vals else "" ,
                'state_id':state_vals.id,
                'zip':values.get('zip'),
                'dob':get_dob,
                'gender':values.get('gender').lower(),
                'location_ids':location_ids.ids if location_ids else False,
                'mobile' : values.get('mobile').split('.')[0],
                'email' : values.get('email'),
                'alternate_mobile' : values.get('alternate_mobile').split('.')[0],
                'alternate_email':values.get('alternate_email'),
                'reffer_type_id':reffer_type_vals.id,
                'company_type':'person',

                    }
            
            res = partner.create(vals)
        # get the new or existing partner id 03-08-33
        cust_rec = 0
        if get_customer:
            for record in get_customer:
                cust_rec = record.id
        else:
            cust_rec = res.id
        count_import = 0
        if not get_contact:
            rec_count = 0
            # get current active id and create the new record in asterisk dialler contract 01-08-22 
            if res:
                create_astrisk_contract = self.env['asterisk_dialer.contact'].create({
                "name" : res.name,
                "phone" : values.get('mobile').split('.')[0],
                'campaign':rec_campaign_id.id,
                'source':'Import',
                'model_object': '{},{}'.format(
                                'res.partner', res.id),
                })
                # get the imported record count 02-08-22
                count_import += len(create_astrisk_contract)
                self.import_count += count_import
        if get_contact:
            # get the exist record and create as the skipped record 02-08-22
            data_skipped_record = self.env['datamine.skipped.records'].create({
                'name':values.get('first_name') +''+values.get('last_name') ,
                'campaign_id':rec_campaign_id.id,
                'mobile':values.get('mobile').split('.')[0],
                'create_date':datetime.today(),
                'source':'New Upload',
                
                })
            # used for invisible the duplicate contact page 09-08-22
            if data_skipped_record:
                rec_campaign_id.duplicate_contact = True
            else:
                rec.rec_campaign_id.duplicate_contact = False

        return res

    # used to create the new customer or merge customer based on the below condition 06-07-22
    def action_merge_contact(self,values):
        get_partner_id = self.env['res.partner'].search([])
        partner_record = self.env['res.partner']
        # country_vals = self.get_country(values)
        state_vals = self.get_state(values)
        city_vals = self.get_city(values)
        reffer_type_vals = self.get_reffer(values)
        # if self.merge_duplicate_cont:
        #   # if excel data is similar to res partner data means call below condition and click merge contacts 07-07-22
        #   # for partner_rec in get_partner_id.filtered(lambda l: l.mobile==values.get('mobile') or l.email==values.get('email')):
        #   #   partner_rec.update({
        #   #       'name' : values.get('name'),
        #   #       'firstname' : values.get('first_name'),
        #   #       'lastname' : values.get('last_name'),
        #   #       'email' : values.get('email'),
        #   #       'mobile' : values.get('mobile').split('.')[0],
        #   #       'country_id':country_vals.id,
        #   #       'state_id':state_vals.id,
        #   #       'city_id':city_vals.id,
        #   #       'gender':values.get('gender'),
        #   #       'reffer_type_id':reffer_type_vals.id,
        #   #       'company_type':'person',
        #   #       # 'is_a_customer':values.get('is_a_customer')
        #   #       'alternate_email':False
        #   #   })
        #   active_id = self._context.get('active_id')
        #   rec_id = self.env["asterisk_dialer.campaign"].browse(active_id)
        #   get_contact = self.env['asterisk_dialer.contact'].search([('phone','ilike',values.get('mobile').split('.')[0]),('campaign','=',rec_id.id)])
        #   if not get_contact:
        #       create_astrisk_contract = self.env['asterisk_dialer.contact'].create({
        #           "name" : values.get('name'),
        #           "phone" : values.get('mobile').split('.')[0],
        #           'campaign':rec_id.id
        #       })
        #       data_skipped_record = self.env['datamine.skipped.records'].create({
     #                'name':values.get('name'),
     #                'campaign_id':rec_id.id,
     #                'mobile':values.get('mobile').split('.')[0],
     #                'create_date':datetime.today(),
     #                'source':'Import'
     #                })
            # if excel data is not similar to res partner data means call below condition and click merge contacts 07-07-22
            # for part_create in get_partner_id.filtered(lambda l: l.mobile != values.get('mobile') and l.email != values.get('email')):
            #   vals = {
            #       'name' : values.get('name'),
            #       'firstname' : values.get('first_name'),
            #       'lastname' : values.get('last_name'),
            #       'email' : values.get('email'),
            #       'mobile' : values.get('mobile').split('.')[0],
            #       'country_id':country_vals.id,
            #       'state_id':state_vals.id,
            #       'city_id':city_vals.id,
            #       'gender':values.get('gender'),
            #       'reffer_type_id':reffer_type_vals.id,
            #       'company_type':'person',
            #       # 'is_a_customer':values.get('is_a_customer')
            #       'alternate_email':False
            #       }
            #   create_vals = partner_record.create(vals)
            #   return create_vals

# get the country 07-07-22
    # def get_country(self,values):
    #   get_country_vals = self.env['res.country'].search([('name','ilike',values.get('country'))])
    #   if get_country_vals:
    #       return get_country_vals
    #   else:
    #       raise UserError('Country is not found in system !')
# get the state 07-07-22
    def get_state(self,values):
        if values.get('state'):
            get_state_vals = self.env['res.country.state'].search([('name','ilike',values.get('state'))])
            if get_state_vals:
                return get_state_vals
            else:

                raise UserError('State is not found in system !')
        else:
            return False

# get the city 07-07-22
    def get_city(self,values):
        if values.get('city'):
            get_city_vals = self.env['city.master'].search([('name','ilike',values.get('city'))])
            if get_city_vals:
                return get_city_vals
            else:
                raise UserError('City is not found in system !')
        else:
            return False
# get the lead source 07-07-22
    def get_reffer(self,values):
        if values.get('lead'):
            get_reffer_vals = self.env['master.refferal'].search([('name','ilike',values.get('lead'))])
            if get_reffer_vals:
                return get_reffer_vals
            else:
                raise UserError((' Lead Source is not found in system !'))
        else:
            return False

    # get the location 24-11-22
    def action_get_location(self,values):
        if values.get('location'):
            get_location = self.env['res.company'].search([('name','ilike',values.get('location'))])
            if get_location:
                return get_location
            else:
                raise UserError((' Location is not found in system !'))
        else:
            return False

    # def get_birth_date(self, values):
    #     birthday_date =" "
    #     if values.get('date_of_birth'):
    #         birthday_date = datetime.strptime(values.get('date_of_birth'), '%Y/%m/%d')
    #     else:
    #         birthday_date = " "
    #     return birthday_date

    def get_birth_date(self, values):
        birthday_date =" "
        # convert the string type into date format
        date = datetime.strptime((values.get('date_of_birth')), '%d-%m-%Y').date()
        # convert ends
        if values.get('date_of_birth'):
            birthday_date = date.strftime('%Y-%m-%d')
        else:
            birthday_date = False
        return birthday_date


    # Generate the sample xls report
    def generate_sample_xls(self):        
        file_name = 'Dataminer Import Sample.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        date_format = xlwt.XFStyle()
        sheet = workbook.add_sheet('Dataminer Import Sample',cell_overwrite_ok=True)
        style_bold_head = xlwt.easyxf("font:bold 1;align:horiz center;font:bold 1")
        for ran in (range(1,20)):
            sheet.col(ran).width = int(20*260)
        sheet.write(0,0, "Firstname",style_bold_head)
        sheet.write(1,0, 'Abc')
        sheet.write(0,1, "Lastname",style_bold_head)
        sheet.write(1,1, 'xyz')
        sheet.write(0,2, "Address",style_bold_head)
        sheet.write(1,2, 'Bin Lootah Building, Al Jaziri Street, Al Muraqqabat, Dubai')
        sheet.write(0,3, "City",style_bold_head)
        sheet.write(1,3, 'Dubai')
        sheet.write(0,4, "State",style_bold_head)
        sheet.write(1,4, 'Dubai')
        sheet.write(0,5, "Zip",style_bold_head)
        sheet.write(1,5, '456547')
        sheet.write(0,6, "Date of Birth",style_bold_head)
        sheet.write(1,6, '21-10-2022')
        sheet.write(0,7, "Gender",style_bold_head)
        sheet.write(1,7, 'Male')
        sheet.write(0,8, "Location",style_bold_head)
        sheet.write(1,8, 'Illuminations Dubai Branch')
        sheet.write(0,9, "Mobile",style_bold_head)
        sheet.write(1,9, '1234567890')
        sheet.write(0,10, "Email",style_bold_head)
        sheet.write(1,10, 'abc123@gmail.com')
        sheet.write(0,11, "Alternate Mobile",style_bold_head)
        sheet.write(1,11, '0987654321')
        sheet.write(0,12, "Alternate Email",style_bold_head)
        sheet.write(1,12, 'xyz123@gmail.com')
        sheet.write(0,13, "Lead Source",style_bold_head)
        sheet.write(1,13, 'website')
        fp = BytesIO()
        workbook.save(fp)
        self.write({'filename': fp, 'excel_file': base64.encodestring(fp.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=import.partner&field=excel_file&download=true&id=%s&filename=%s' % (self.id, file_name),
            'target': 'new',
        } 
        

class SuccessMeassage(models.TransientModel):
    _name = 'success.message'
    _description = 'Success Message'

    name = fields.Char(string="Name")
    file = fields.Char(string="File")
    total_count = fields.Integer(string="Total Import Records")
    import_count = fields.Integer(string="Import Count")
    skipped_count = fields.Integer(string="Skipped Count")

    # using to cancel the wizard 06-07-22
    def action_done(self):
        return True
