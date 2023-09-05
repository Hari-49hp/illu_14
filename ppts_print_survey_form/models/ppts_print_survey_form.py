# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class PrintSurvey(models.Model):
    """Inherit Survey model and enable the print option"""
    _inherit = "survey.survey"

    def print_report(self):

        return self.env.ref(
            'ppts_print_survey_form.action_print_survey').report_action(self, data='')


class SurveyFormPrint(models.AbstractModel):
    """Class for print the Qweb report"""
    _name = 'report.ppts_print_survey_form.ppts_print_survey_form'
    _description ="SurveyFormPrint"

    @api.model
    def _get_report_values(self, docids, data):
        for move in self.env['survey.survey'].search([('id', 'in', docids)]):
            print(move)
        docs = self.env.context.get('active_ids')
        if docs == None:
            docs = docids
        return {
            'data': self.env['survey.survey'].search([('id', 'in', docs)])
        }
