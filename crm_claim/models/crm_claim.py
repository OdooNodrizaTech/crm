# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.tools import html2plaintext
from odoo.addons.base.res.res_request import referenceable_models

import logging

_logger = logging.getLogger(__name__)

class CrmClaim(models.Model):
    _name = "crm.claim"
    _description = "Reclamacion"
    _order = "date desc"
    _inherit = ['mail.thread']
    
    code = fields.Char(
        string='Numero',
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )
    name = fields.Char(
        compute='_get_name',
        store=False
    )
    active = fields.Boolean(
        default=True,
    )    
    description = fields.Text()
    resolution = fields.Text()
    quality_observations = fields.Text()    
    date_closed = fields.Datetime(
        string='Fecha cierre'
    )
    date = fields.Datetime(
        string='Fecha',
        index=True,
        default=fields.Datetime.now
    )
    categ_id = fields.Many2one(
        comodel_name='crm.claim.category',
        string='Tipo de reclamacion',
    )
    model_ref_id = fields.Reference(
        #selection=referenceable_models,
        selection=[('sale.order','Pedido de venta'),('res.partner','Empresa'),('account.invoice','Factura'),('product.product','Producto')],
        string='Referencia',
        oldname='ref',
    )
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Transportista',
        store=True
    )    
    org_id = fields.Many2one(
        comodel_name='crm.claim.origin',
        string='Origen',
    )
    org_other_show = fields.Boolean(
        compute='_get_org_other_show',
        store=False
    )
    org_other = fields.Char(
        string='Otro',
    )    
    corrective_action = fields.Boolean(
        string="Necesita accion correctiva"
    )    
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        default=lambda self: self.env.user,
    )    
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        default=lambda self: self.env.user.company_id,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
    )   
    stage_id = fields.Many2one(
        comodel_name='crm.claim.stage',
        string='Etapa',
        track_visibility='onchange',
        default=1,
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        compute='_get_order_id',
        string='Reposicion'
    )
    
    _sql_constraints = [
        ('crm_claim_unique_code', 'UNIQUE (code)',
         'El codigo debe ser unico'),
    ]
    
    @api.onchange('org_id')
    def change_org_id(self):
        self._get_org_other_show()
        
    @api.one        
    def _get_name(self):
        self.name = self.code                      
    
    @api.one        
    def _get_order_id(self):
        if self.id!=False:
            sale_order_ids = self.env['sale.order'].search(
                [                
                    ('claim', '=', True),
                    ('claim_id', '=', self.id)
                 ])
            
            if sale_order_ids!=False:                
                for sale_order_id in sale_order_ids:                        
                    self.order_id = sale_order_id    
    
    @api.one        
    def _get_org_other_show(self):          
        self.org_other_show = False
        if self.org_id.id!=False and self.org_id.other==True:
            self.org_other_show = True

    @api.onchange('model_ref_id')
    def change_model_ref_id(self):
        self.carrier_id = False # Fix default

        if self.model_ref_id != False:
            if self.model_ref_id._name == 'sale.order':
                if self.model_ref_id.id > 0:
                    if self.model_ref_id.carrier_id.id > 0:
                        self.carrier_id = self.model_ref_id.carrier_id.id
    
    @api.model
    def create(self, values):
        if values.get('code', '/') == '/':
            values['code'] = self.env['ir.sequence'].next_by_code('crm.claim')
            
        if 'model_ref_id' in values and values.get('model_ref_id')!=False:
            model_ref_name, model_ref_id  = values.get('model_ref_id').split(',')    
            if model_ref_name=='res.partner':
                values['partner_id'] = model_ref_id
            elif model_ref_name=='sale.order' or model_ref_name=='purchase.order' or model_ref_name=='account.invoice':
                model_ref_search_ids = self.env[model_ref_name].search([('id', '=', model_ref_id)])[0]
                values['partner_id'] = model_ref_search_ids.partner_id.id
                values['carrier_id'] = model_ref_search_ids.carrier_id.id            
            
        return super(CrmClaim, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('resolution') != False and self.date_closed == False:
            values['date_closed'] = fields.datetime.now()

        if 'model_ref_id' in values and values.get('model_ref_id') != False:
            model_ref_name, model_ref_id = values.get('model_ref_id').split(',')
            if model_ref_name == 'res.partner':
                values['partner_id'] = model_ref_id
            elif model_ref_name == 'sale.order' or model_ref_name == 'purchase.order' or model_ref_name == 'account.invoice':
                model_ref_search_ids = self.env[model_ref_name].search([('id', '=', model_ref_id)])[0]
                values['partner_id'] = model_ref_search_ids.partner_id.id
        #return
        return super(CrmClaim, self).write(values)