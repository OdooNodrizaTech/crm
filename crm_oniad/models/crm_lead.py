# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
_logger = logging.getLogger(__name__)

from odoo import api, models, fields, _
from odoo.exceptions import Warning
from datetime import datetime

import uuid

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    done_user_id = fields.Many2one(
        comodel_name='res.users',        
        string='User done'
    )
    day_deadline = fields.Float(
        compute='_compute_day_deadline', 
        string='Days for the planned closing',
        store=True
    )
    website = fields.Char(
        string='Website'
    )
    marketing_campaign = fields.Boolean( 
        string='Campana de marketing'
    )    
    activities_count = fields.Integer(
        compute='_compute_activities_count',
        string="Actividades",
    )
    commercial_activity_type = fields.Selection(
        selection=[
            ('account','Account'), 
            ('hunter','Hunter')                          
        ],
        string='Commercial activity type'
    )
    register_token = fields.Char(
        string='Register token',
        copy=False,
        default=lambda self: str(uuid.uuid4()),
        required=True
    )
    crm_lead_source_id = fields.Many2one(
        comodel_name='crm.lead.source',
        string='Crm Lead Source'
    )
    lead_oniad_type = fields.Selection(
        selection=[
            ('welcome','Bienvenida'), 
            ('sleep','Dormido'), 
            ('catchment','Captacion'),
            ('other','Otro')                         
        ],
        string='Lead type'
    )                                        
    
    @api.onchange('type')
    def onchange_type(self):
        if self._origin.id==False:        
            if self.type=='lead':
                self.commercial_activity_type = 'hunter'
                self.lead_oniad_type = 'catchment'
            else:
                self.commercial_activity_type = 'account'
                self.lead_oniad_type = 'other'

    @api.model
    def create(self, values):
        allow_create = True
                                
        value_type = values.get('type')
        value_commercial_activity_type = values.get('commercial_activity_type')
        value_lead_oniad_type = values.get('lead_oniad_type')
                
        if value_type=='lead':
            if value_commercial_activity_type!='hunter':
                allow_create = False
                raise Warning(_("An lead must have the type of commercial activity 'Hunter'"))
                
            if allow_create==True and value_lead_oniad_type!='catchment':
                allow_create = False
                raise Warning(_("An lead must have the type of lead to 'Capture'"))
        else:
            if value_commercial_activity_type!='account':
                allow_create = False
                raise Warning(_("A opportunity must have the business type 'Account'"))
                
            if allow_create==True and value_lead_oniad_type=='catchment':
                allow_create = False
                raise Warning(_("A opportunity must not have the lead type 'Capture'"))
    
        if allow_create==True:
            return_val = super(CrmLead, self).create(values)
            return return_val
                
    @api.multi
    def _compute_activities_count(self):
        activity_data = self.env['crm.activity.report'].read_group([('lead_id', 'in', self.ids)], ['lead_id'], ['lead_id'])
        mapped_data = {act['lead_id'][0]: act['lead_id_count'] for act in activity_data}
        for lead in self:
            lead.activities_count = mapped_data.get(lead.id, 0)                
                    
    @api.one
    def convert_opportunity_create_partner(self, user_ids=False, team_id=False):
        if self.type=='lead':            
            result_partner_ids = super(CrmLead, self).handle_partner_assignation('create', False)
            partner_id = result_partner_ids[self.id]
            return super(CrmLead, self).convert_opportunity(partner_id, user_ids, team_id)
        else:
            return False
            
    @api.multi
    def _lead_create_contact(self, name, is_company, parent_id=False):
        return_def = super(CrmLead, self)._lead_create_contact(name, is_company, parent_id)
        return_def.website = self.website
        return return_def    
    
    @api.multi
    def action_set_won(self):
        #done_user_id
        for lead in self:
            lead.done_user_id = lead.user_id
        #super
        return super(CrmLead, self).action_set_won()                                                                    
                
    @api.depends('date_deadline')
    def _compute_day_deadline(self):
        for lead in self:
            if lead.date_deadline!=False:
                current_date = fields.Datetime.from_string(str(datetime.today().strftime("%Y-%m-%d")))
                date_deadline = fields.Datetime.from_string(lead.date_deadline)        
                lead.day_deadline = (date_deadline - current_date).days                                                          