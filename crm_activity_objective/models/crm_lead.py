# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, models, fields
from openerp.exceptions import Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    next_activity_objective_id = fields.Many2one(
        comodel_name='crm.activity.objective',
        track_visibility='onchange',
        string='Objetivo de actividad'
    )        
    
    @api.multi    
    def cron_odoo_crm_lead_change_empty_next_activity_objective_id(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_empty_next_activity_objective_id')                
    
    @api.multi    
    def cron_odoo_crm_lead_change_seguimiento(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_seguimiento')                                                                            
    
    @api.multi    
    def cron_odoo_crm_lead_change_dormidos(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_dormidos')                    
                    
    @api.model    
    def action_boton_pedir_dormido(self):        
        _logger.info('action_boton_pedir_dormido')                                                                                                    
    
    @api.multi    
    def cron_odoo_crm_lead_change_inactivos(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_inactivos')                           
    
    @api.model                        
    def action_boton_pedir_activo(self):
        _logger.info('action_boton_pedir_activo')                                                                    