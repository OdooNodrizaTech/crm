# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import Warning
from dateutil.relativedelta import relativedelta
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'
        
    lead_m2 = fields.Float(        
        string="Lead m2",
        readonly=True
    )
    comment_customer = fields.Char(
        string='Comentarios Cliente',
        size=80
    )            
    partner_id_user_id = fields.Many2one(
        comodel_name='res.users',        
        compute='_get_partner_id_user_id',
        store=False,
        string='Comercial cliente'
    )        
    
    @api.model        
    def _get_date_deadline_override(self):
        current_date = datetime.today()
        date_deadline_end = current_date + relativedelta(days=90)
        return date_deadline_end.strftime("%Y-%m-%d")
    
    date_deadline_override = fields.Date(
        default=_get_date_deadline_override,
        string='Cierre previsto', 
        store=False
    )
            
    @api.one        
    def _get_partner_id_user_id(self):
        for obj in self:
            obj.partner_id_user_id = False
            if obj.partner_id.id>0:
                obj.partner_id_user_id = obj.partner_id.user_id.id
                
    @api.onchange('user_id')
    def function_custom_user_id(self):
        #operations
        if self._origin.id>0 and self.user_id.id>0:                                             
            self.fix_update_team_id()            
            #user_id
            if self.partner_id.id>0:
                if self.partner_id.user_id.id==0 or self.partner_id.user_id.id==False:
                    self.partner_id.write({
                        'user_id': self.user_id.id
                    })
        
    @api.one
    def fix_update_team_id(self):        
        crm_team_ids = self.env['crm.team'].search([('ar_qt_activity_type', '=', self.ar_qt_activity_type)])
        if crm_team_ids!=False:
            team_modify = False
            for crm_team_id in crm_team_ids:                                                    
                if crm_team_id.ar_qt_customer_type!=False and crm_team_id.ar_qt_customer_type==self.ar_qt_customer_type:
                    self.team_id = crm_team_id.id
                    team_modify = True
                else:
                    if team_modify==False:
                        self.team_id = crm_team_id.id
                        
    @api.model
    def create(self, values):
        allow_create = True        
        #prevent without date_deadline or 90 days
        if values['ar_qt_customer_type']!='profesional':
            if 'date_deadline_override' in values:
                values['date_deadline'] = values['date_deadline_override']            
            #date_deadline
            if 'date_deadline' not in values:
                allow_create = False
                raise Warning("Es necesario definir una fecha de cierre previsto para poder crear el flujo")
            else:                                                                                         
                if values['date_deadline']==False:
                    allow_create = False
                    raise Warning("Es necesario definir una fecha de cierre previsto para poder crear el flujo")            
                else:
                    current_date = fields.Datetime.from_string(str(datetime.today().strftime("%Y-%m-%d")))
                    days_difference = (fields.Datetime.from_string(values.get('date_deadline'))-current_date).days
                    if days_difference>90:
                        allow_create = False
                        raise Warning("El cierre previsto no puede ser superior a 90 dias ni anterior a la fecha actual ("+str(days_difference)+") al crear")
        #operations
        if allow_create==True:    
            return super(CrmLead, self).create(values)                                            
    
    @api.multi
    def write(self, vals):                              
        allow_write = True
        if self.id>0:
            #validation date_deadline and 90 days
            if self.ar_qt_customer_type!='profesional':
                if 'date_deadline' in vals:
                    if vals['date_deadline']==False:
                        allow_write = False
                        raise Warning("Es necesario definir una fecha de cierre previsto para poder editar el flujo")
                    else:                        
                        current_date = fields.Datetime.from_string(str(datetime.today().strftime("%Y-%m-%d")))
                        days_difference = (fields.Datetime.from_string(vals['date_deadline'])-current_date).days
                        if days_difference>90:
                            allow_write = False
                            raise Warning("El cierre previsto no puede ser superior a 90 dias ni anterior a la fecha actual ("+str(days_difference)+") al editar")            
            #operations
            if allow_write==True:
                #check user_id
                if 'user_id' in vals and self.user_id.id==0 and vals['user_id']>0:
                    sale_order_ids = self.env['sale.order'].search([('opportunity_id', '=', self.id)])
                    if sale_order_ids!=False:
                        for sale_order_id in sale_order_ids:
                            if sale_order_id.user_id.id==0:
                                #update date_order
                                current_date = datetime.today()
                                sale_order_id.date_order = current_date.strftime("%Y-%m-%d %H:%M:%S")                
        #allow_write
        if allow_write==True:                                      
            return_object = super(CrmLead, self).write(vals)        
            #fix tags                                 
            if 'tag_ids' in vals and self.tag_ids!=False:
                tag_ids = []    
                for tag_id in self.tag_ids:
                    tag_ids.append(tag_id.id)                        
                
                if self.id>0:
                    sale_order_ids = self.env['sale.order'].search([('opportunity_id', '=', self.id)])
                    for sale_order in sale_order_ids:                    
                        tag_ids2 = []
                        for tag_id2 in sale_order.tag_ids:
                            tag_ids2.append(tag_id2.id)
                        
                        for tag_id in tag_ids:
                            if not tag_id in tag_ids2:
                                tag_ids2.append(tag_id)
                        
                        sale_order.tag_ids = self.env['crm.lead.tag'].search([('id', 'in', tag_ids2)])                                                                                                                
            #return                                                                    
            return return_object                                                        