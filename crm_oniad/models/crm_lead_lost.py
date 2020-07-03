# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import _, api, exceptions, fields, models

import logging
_logger = logging.getLogger(__name__)

class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'        

    survey_url = fields.Char(
        string='Encuesta',
        store=False
    )
    
        
    @api.model
    def default_get(self, fields):
        res = super(CrmLeadLost, self).default_get(fields)                    
                                    
        lead_obj_return = self.env['crm.lead'].search([('id', '=', self.env.context.get('active_id'))])
        if lead_obj_return.id>0:
            survey_url = False
            
            if lead_obj_return.lead_oniad_type=='welcome':
                survey_url = self.env['ir.config_parameter'].sudo().get_param('crm_oniad_survey_url_lead_oniad_type_welcome')            
            elif lead_obj_return.lead_oniad_type=='sleep':
                survey_url = self.env['ir.config_parameter'].sudo().get_param('crm_oniad_survey_url_lead_oniad_type_sleep')            
            elif lead_obj_return.lead_oniad_type=='catchment':
                survey_url = self.env['ir.config_parameter'].sudo().get_param('crm_oniad_survey_url_lead_oniad_type_catchment')
            
            if survey_url!=False:
                survey_url = survey_url.replace('[odoo_lead_id_value]', str(lead_obj_return.id))
                                                    
            res['survey_url'] = survey_url          
            
        return res                                                