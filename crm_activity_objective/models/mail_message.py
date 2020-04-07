# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    activity_objective_id = fields.Many2one(
        comodel_name='crm.activity.objective',
        string='Objetivo de actividad'
    )

    @api.model
    def _create(self, values):
        return_id = super(MailMessage, self)._create(values)
        mail_message_ids = self.env['mail.message'].sudo().search([('id', '=', return_id)])
        if len(mail_message_ids) > 0:
            mail_message_id = mail_message_ids[0]
            if mail_message_id.id>0:
                #operations
                if mail_message_id.model=='sale.order':
                    model_res_id = self.env[mail_message_id.model].sudo().browse(mail_message_id.res_id)
                    if model_res_id.opportunity_id.id>0:
                        if model_res_id.opportunity_id.next_activity_objective_id.id>0:
                            mail_message_id.activity_objective_id = model_res_id.opportunity_id.next_activity_objective_id.id

                elif mail_message_id.model=='crm.lead':
                    model_res_id = self.env[mail_message_id.model].sudo().browse(mail_message_id.res_id)
                    if model_res_id.next_activity_objective_id.id>0:
                        mail_message_id.activity_objective_id = model_res_id.next_activity_objective_id.id
                #fix mail.message.little
                mail_message_little_vals = {
                    'mail_message_id': mail_message_id.id,
                    'subtype_id': mail_message_id.subtype_id.id,
                    'res_id': mail_message_id.res_id,
                    'date': mail_message_id.date,
                    'author_id': mail_message_id.author_id.id,
                    'model': mail_message_id.model,
                    'message_type': mail_message_id.message_type,
                    'duration': mail_message_id.duration
                }
                #parent_id
                if mail_message_id.parent_id.id>0:
                    mail_message_little_vals['parent_id'] = mail_message_id.parent_id.id
                #activity_objective_id
                if mail_message_id.activity_objective_id.id>0:
                    mail_message_little_vals['activity_objective_id'] = mail_message_id.activity_objective_id.id
                #create
                mail_message_little_obj = self.env['mail.message.little'].sudo().create(mail_message_little_vals)                                        
        #return_id                    
        return return_id