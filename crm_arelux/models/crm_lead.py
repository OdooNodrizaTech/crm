# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime
import pytz

import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    activities_count = fields.Integer(
        compute='_compute_activities_count',
        string="Actividades",        
    )
    crm_activity_ids = fields.One2many('crm.activity.report', 'lead_id', string='Actividades')    
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id
    )
    lead_m2 = fields.Float(        
        string="Lead m2",
        readonly=True
    )
    comment_customer = fields.Char(
        string='Comentarios Cliente',
        size=80
    )
    date_action = fields.Datetime(
        string='Fecha siguiente actividad', 
        index=True
    )
    partner_id_total_sale_order = fields.Integer(
        compute='_partner_id_total_sale_order',
        string="Nº Pedidos (cliente)",        
    )
    total_sale_order = fields.Integer(
        string="Nº Pedidos (oport)",
        help="Nº pedidos > 300€ de ese cliente (Flujo)",
        default=0,
        readonly=True
    )    
    total_sale_order_last_30_days = fields.Integer(
        string="Nº pedidos 30 dias",
        help="Nº pedidos (>300€) de los ultimos 30 dias",
        default=0,
        readonly=True
    )
    total_sale_order_last_90_days = fields.Integer(
        string="Nº pedidos 90 dias",
        help="Nº pedidos (>300€) de los ultimos 90 dias",
        default=0,
        readonly=True
    )
    total_sale_order_last_12_months = fields.Integer(
        string="Nº pedidos 12 meses",
        help="Nº pedidos (>300€) de los ultimos 12 meses",
        default=0,
        readonly=True
    )
    partner_id_account_invoice_amount_untaxed_total = fields.Monetary(
        compute='_partner_id_account_invoice_amount_untaxed_total',
        string="Facturación (cliente)"
    )
    account_invoice_amount_untaxed_total = fields.Monetary(
        string="Facturación (oport)",
        help="Historico de facturacion (BI) de ese cliente (Flujo)",
        readonly=True
    )
    days_from_last_sale_order = fields.Integer(
        string="Dias desde pto",
        help="Nº de dias desde el ultimo presupuesto enviado",
        default=0,
        readonly=True
    )
    date_from_last_sale_order = fields.Date(
        string="Fecha desde pto",
        readonly=True
    )
    days_from_last_message = fields.Integer(
        string="Dias desde contacto",
        help="Nº de dias desde el ultimo contacto (Generalmente mensaje enviado como remitente el comercial)",#Fix para evitar facturas
        default=0,
        readonly=True
    )
    date_from_last_message = fields.Date(
        string="Fecha desde contacto",
        readonly=True
    )
    next_activity_objective_id = fields.Many2one(
        comodel_name='crm.activity.objective',
        track_visibility='onchange',
        string='Objetivo de actividad'
    )
    
    @api.one
    def clean_next_activity(self):
        #next_activity_id
        if self.next_activity_id.id>0:
            self.next_activity_id = False
        #date_action
        if self.date_action!=False:
            self.date_action = False
        #title_action
        if self.title_action!=False:
            self.title_action = False
    
    @api.multi
    def action_set_won(self):
        for obj in self:
            obj.clean_next_activity()
        #action_set_won                
        return super(CrmLead, self).action_set_won()
        
    @api.multi
    def action_set_lost(self):
        #done_user_id
        for lead in self:
            lead.clean_next_activity()
        #super            
        return super(CrmLead, self).action_set_lost()                

    @api.depends('crm_activity_ids')    
    def _compute_activities_count(self):
        for lead in self:
            lead.activities_count = len(lead.crm_activity_ids)                    
    
    @api.depends('partner_id')
    def _partner_id_total_sale_order(self):
        for lead in self:
            if lead.partner_id.id>0:
                lead.partner_id_total_sale_order = lead.partner_id.total_sale_order
                
    @api.depends('partner_id')
    def _partner_id_account_invoice_amount_untaxed_total(self):
        for lead in self:
            if lead.partner_id.id>0:
                lead.partner_id_account_invoice_amount_untaxed_total = lead.partner_id.account_invoice_amount_untaxed_total                    
            
    @api.multi    
    def cron_odoo_crm_lead_fields_generate(self, cr=None, uid=False, context=None):
        _logger.info('sql_1 (total_sale_order,total_sale_order_last_30_days,total_sale_order_last_90_days, date_from_last_sale_order)')
        self._cr.execute("""
            UPDATE crm_lead SET (total_sale_order, total_sale_order_last_30_days, total_sale_order_last_90_days, total_sale_order_last_12_months, date_from_last_sale_order) = (
            	SELECT clr.total_sale_order, total_sale_order_last_30_days, total_sale_order_last_90_days, total_sale_order_last_12_months, last_date_order_management 
            	FROM crm_lead_report AS clr 
            	WHERE clr.lead_id = crm_lead.id
            ) 
            WHERE crm_lead.id IN (
            	SELECT clr2.lead_id 
            	FROM crm_lead_report AS clr2 
            	LEFT JOIN crm_lead AS cl ON clr2.lead_id = cl.id 
            	WHERE (
            		(cl.total_sale_order <> clr2.total_sale_order) 
            		OR (cl.total_sale_order_last_30_days <> clr2.total_sale_order_last_30_days) 
            		OR (cl.total_sale_order_last_90_days <> clr2.total_sale_order_last_90_days)
                    OR (cl.total_sale_order_last_12_months  <> clr2.total_sale_order_last_12_months )                    
            		OR (cl.date_from_last_sale_order IS NOT NULL AND cl.date_from_last_sale_order <> clr2.last_date_order_management) 
            		OR (cl.date_from_last_sale_order IS NULL AND clr2.last_date_order_management IS NOT NULL)
            	) 
            	LIMIT 1000
            )
        """)
        _logger.info('sql_2 (account_invoice_amount_untaxed_total)')
        self._cr.execute("""
            UPDATE crm_lead SET (account_invoice_amount_untaxed_total) = (
            	SELECT ROUND((clair.amount_untaxed_total_out_invoice-clair.amount_untaxed_total_out_refund)::numeric,2)::float 
            	FROM crm_lead_account_invoice_report AS clair 
            	WHERE clair.lead_id = crm_lead.id
            ) 
            WHERE crm_lead.id IN (
            	SELECT clair2.lead_id 
                FROM crm_lead_account_invoice_report AS clair2 
                LEFT JOIN crm_lead AS cl ON clair2.lead_id = cl.id 
                WHERE (clair2.amount_untaxed_total_out_invoice IS NOT NULL OR clair2.amount_untaxed_total_out_refund IS NOT NULL) 
                AND (
                	(
                	cl.account_invoice_amount_untaxed_total IS NOT NULL
                	AND (ROUND((clair2.amount_untaxed_total_out_invoice-clair2.amount_untaxed_total_out_refund)::numeric,2)::float <> cl.account_invoice_amount_untaxed_total)
                	)
                	OR cl.account_invoice_amount_untaxed_total IS NULL
                ) 
            	LIMIT 1000
            )
        """)        
        _logger.info('sql_3 (date_from_last_message)')
        self._cr.execute("""
        	SELECT clmmr2.lead_id, clmmr2.date 
        	FROM crm_lead_mail_message_report AS clmmr2 
        	LEFT JOIN crm_lead AS cl ON clmmr2.lead_id = cl.id 
        	WHERE (
        		(cl.date_from_last_message IS NOT NULL AND clmmr2.date  <> cl.date_from_last_message) 
        		OR (cl.date_from_last_message IS NULL AND clmmr2.date IS NOT NULL)
        	)
            AND clmmr2.lead_id > 0
        	LIMIT 1000            
        """)
        items = self._cr.fetchall()
        if len(items)>0:
            for item in items:
                self._cr.execute("""UPDATE crm_lead SET date_from_last_message = '"""+str(item[1])+"""' WHERE id = """+str(item[0]))                
        
        _logger.info('sql_4 (mobile, phone)')
        self._cr.execute("""                
            UPDATE crm_lead SET (mobile, phone) = (
            	SELECT rp.mobile, rp.phone
            	FROM res_partner AS rp
            	WHERE crm_lead.partner_id = rp.id
            ) 
            WHERE crm_lead.id IN (
            	SELECT cl.id 
            	FROM crm_lead AS cl
            	LEFT JOIN res_partner AS rp ON cl.partner_id = rp.id
            	WHERE cl.partner_id IS NOT NULL
            	AND (rp.mobile IS NOT NULL OR rp.phone IS NOT NULL)
            	AND (
            		(rp.mobile IS NOT NULL AND cl.mobile IS NULL)
            		OR (rp.mobile IS NOT NULL AND cl.mobile IS NOT NULL AND rp.mobile <> cl.mobile)
            		OR (rp.phone IS NOT NULL AND cl.phone IS NULL)
            		OR (rp.phone IS NOT NULL AND cl.phone IS NOT NULL AND rp.phone <> cl.phone)
            	) 
            	LIMIT 1000
            )
        """)            
        
    @api.multi    
    def cron_odoo_crm_lead_fields_generate_days(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_fields_generate_days')
        _logger.info('sql_1 (days_from_last_sale_order)')
        self._cr.execute("""
            UPDATE crm_lead SET (days_from_last_sale_order) = (
            	SELECT(NOW()::date - cl.date_from_last_sale_order) 
            	FROM crm_lead AS cl 
            	WHERE cl.id = crm_lead.id
            ) 
            WHERE crm_lead.date_from_last_sale_order IS NOT NULL
        """)  
        _logger.info('sql_2 (days_from_last_message)')
        self._cr.execute("""
            UPDATE crm_lead SET (days_from_last_message) = (
            	SELECT(NOW()::date - cl.date_from_last_message) 
            	FROM crm_lead AS cl 
            	WHERE cl.id = crm_lead.id
            ) 
            WHERE crm_lead.date_from_last_message IS NOT NULL
        """)        
    
    @api.multi    
    def cron_odoo_crm_lead_change_empty_next_activity_objective_id(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_empty_next_activity_objective_id')
        self.cron_odoo_crm_lead_change_empty_next_activity_objective_id_todocesped()#Todocesped
        self.cron_odoo_crm_lead_change_empty_next_activity_objective_id_arelux()#Arelux
        
    @api.multi    
    def cron_odoo_crm_lead_change_empty_next_activity_objective_id_todocesped(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_empty_next_activity_objective_id_todocesped')
        #ar_qt_todocesped_pf_customer_type=False
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', '=', 'activation'),
                ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.ar_qt_todocesped_pf_customer_type', '=', False),
                ('partner_id.total_sale_order', '=', 0),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]                        
        )        
        #operations
        if len(crm_lead_ids)>0:
            for crm_lead_id in crm_lead_ids:
                crm_lead_id.next_activity_objective_id = False
        #ar_qt_todocesped_pf_customer_type=other
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', '=', 'activation'),
                ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.ar_qt_todocesped_pf_customer_type', '=', 'other'),
                ('partner_id.total_sale_order', '=', 0),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )        
        #operations
        if len(crm_lead_ids)>0:
            for crm_lead_id in crm_lead_ids:
                crm_lead_id.next_activity_objective_id = False
                
    @api.multi    
    def cron_odoo_crm_lead_change_empty_next_activity_objective_id_arelux(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_empty_next_activity_objective_id_arelux')
        #ar_qt_arelux_pf_customer_type=False
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', '=', 'activation'),
                ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.ar_qt_arelux_pf_customer_type', '=', False),
                ('partner_id.total_sale_order', '=', 0),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]                        
        )        
        #operations
        if len(crm_lead_ids)>0:
            for crm_lead_id in crm_lead_ids:
                crm_lead_id.next_activity_objective_id = False
        #ar_qt_arelux_pf_customer_type=other
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', '=', 'activation'),
                ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.ar_qt_arelux_pf_customer_type', '=', 'other'),
                ('partner_id.total_sale_order', '=', 0),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )        
        #operations
        if len(crm_lead_ids)>0:
            for crm_lead_id in crm_lead_ids:
                crm_lead_id.next_activity_objective_id = False                
    
    @api.multi    
    def cron_odoo_crm_lead_change_seguimiento(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_seguimiento')
        self.cron_odoo_crm_lead_change_seguimiento_todocesped()#Todocesped
        self.cron_odoo_crm_lead_change_seguimiento_arelux()#Arelux
    
    @api.multi    
    def cron_odoo_crm_lead_change_seguimiento_todocesped(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_seguimiento_todocesped')        
        #search
        current_date = datetime.now(pytz.timezone('Europe/Madrid'))
        current_date_month = current_date.strftime("%m")
        
        if current_date_month in ['03', '04', '05', '06', '07', '08']:
            crm_lead_ids = self.env['crm.lead'].search(
                [
                    ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'tracking')),
                    ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                    ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                    ('partner_id.total_sale_order_last_30_days', '>', 0),
                    ('type', '=', 'opportunity'),
                    ('active', '=', True),
                    ('probability', '>', 0),
                    ('probability', '<', 100)
                ]
            )
        else:        
            crm_lead_ids = self.env['crm.lead'].search(
                [
                    ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'tracking')),
                    ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                    ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                    ('partner_id.total_sale_order_last_90_days', '>', 0),
                    ('type', '=', 'opportunity'),
                    ('active', '=', True),
                    ('probability', '>', 0),
                    ('probability', '<', 100)
                ]
            )
        #tracking
        crm_activity_objective_ids_tracking = self.env['crm.activity.objective'].search([('objective_type', '=', 'tracking')])
        if len(crm_activity_objective_ids_tracking)>0:
            crm_activity_objective_id_tracking = crm_activity_objective_ids_tracking[0]
            #operations
            if len(crm_lead_ids)>0:
                for crm_lead_id in crm_lead_ids:
                    crm_lead_id.next_activity_objective_id = crm_activity_objective_id_tracking.id
                    
    @api.multi    
    def cron_odoo_crm_lead_change_seguimiento_arelux(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_seguimiento_arelux')        
        #search
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'tracking')),
                ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.total_sale_order_last_90_days', '>', 0),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )
        #tracking
        crm_activity_objective_ids_tracking = self.env['crm.activity.objective'].search([('objective_type', '=', 'tracking')])
        if len(crm_activity_objective_ids_tracking)>0:
            crm_activity_objective_id_tracking = crm_activity_objective_ids_tracking[0]
            #operations
            if len(crm_lead_ids)>0:
                for crm_lead_id in crm_lead_ids:
                    crm_lead_id.next_activity_objective_id = crm_activity_objective_id_tracking.id                                                                            
    
    @api.multi    
    def cron_odoo_crm_lead_change_dormidos(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_dormidos')
        self.cron_odoo_crm_lead_change_dormidos_todocesped()#Todocesped
        self.cron_odoo_crm_lead_change_dormidos_arelux()#Arelux
                
    @api.multi    
    def cron_odoo_crm_lead_change_dormidos_todocesped(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_dormidos_todocesped')
        #search
        current_date = datetime.now(pytz.timezone('Europe/Madrid'))
        current_date_month = current_date.strftime("%m")
        
        if current_date_month in ['03', '04', '05', '06', '07', '08']:
            crm_lead_ids = self.env['crm.lead'].search(
                [
                    ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'wake')),
                    ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                    ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                    ('partner_id.total_sale_order_last_30_days', '=', 0),
                    ('partner_id.total_sale_order', '>', 0),
                    ('type', '=', 'opportunity'),
                    ('active', '=', True),
                    ('probability', '>', 0),
                    ('probability', '<', 100)
                ]
            )
        else:        
            crm_lead_ids = self.env['crm.lead'].search(
                [
                    ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'wake')),
                    ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                    ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                    ('partner_id.total_sale_order_last_90_days', '=', 0),
                    ('partner_id.total_sale_order', '>', 0),
                    ('type', '=', 'opportunity'),
                    ('active', '=', True),
                    ('probability', '>', 0),
                    ('probability', '<', 100)
                ]
            )
        #wake
        crm_activity_objective_ids_wake = self.env['crm.activity.objective'].search([('objective_type', '=', 'wake')])
        if len(crm_activity_objective_ids_wake)>0:
            crm_activity_objective_id_wake = crm_activity_objective_ids_wake[0]
            #operations
            if len(crm_lead_ids)>0:
                for crm_lead_id in crm_lead_ids:
                    crm_lead_id.next_activity_objective_id = crm_activity_objective_id_wake.id
                    
    @api.multi    
    def cron_odoo_crm_lead_change_dormidos_arelux(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_dormidos_arelux')
        #search        
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'wake')),
                ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.total_sale_order_last_90_days', '=', 0),
                ('partner_id.total_sale_order', '>', 0),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )
        #wake
        crm_activity_objective_ids_wake = self.env['crm.activity.objective'].search([('objective_type', '=', 'wake')])
        if len(crm_activity_objective_ids_wake)>0:
            crm_activity_objective_id_wake = crm_activity_objective_ids_wake[0]
            #operations
            if len(crm_lead_ids)>0:
                for crm_lead_id in crm_lead_ids:
                    crm_lead_id.next_activity_objective_id = crm_activity_objective_id_wake.id                    
                    
    @api.model    
    def action_boton_pedir_dormido(self):        
        current_date = datetime.now(pytz.timezone('Europe/Madrid'))
        current_date + relativedelta(hours=2)
        
        response = {
            'errors': True,
            'error': "No tienes flujos de objetivo Despertar sin siguiente actividad para poder asignarte"
        }
                   
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', '=', 'wake'),
                ('user_id', '=', self._uid),
                ('date_action', '=', False),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )
        if len(crm_lead_ids)>0:
            crm_lead_id = False
            #criterio_1            
            crm_lead_ids_criterio_1 = self.env['crm.lead'].search(
                [
                    ('id', 'in', crm_lead_ids.ids),
                    ('partner_id.total_sale_order_last_12_months', '>', 2)
                ],
                order='total_sale_order_last_12_months desc'
            )
            if len(crm_lead_ids_criterio_1)>0:
                crm_lead_id = crm_lead_ids_criterio_1[0]
            #criterio_2
            if crm_lead_id==False:
                #criterio_2 (Todocesped)
                crm_lead_ids_criterio_2_todocesped = self.env['crm.lead'].search(
                    [
                        ('id', 'in', crm_lead_ids.ids),
                        ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                        ('partner_id.total_sale_order_last_12_months', '>', 0),
                        ('ar_qt_todocesped_pf_customer_type', 'in', ('gardener','pool','multiservice','warehouse_construction','nursery'))
                    ],
                    order='total_sale_order_last_12_months desc'                
                )
                if len(crm_lead_ids_criterio_2_todocesped)>0:
                    crm_lead_id = crm_lead_ids_criterio_2_todocesped[0]
                #criterio_2 (Arelux)
                crm_lead_ids_criterio_2_arelux = self.env['crm.lead'].search(
                    [
                        ('id', 'in', crm_lead_ids.ids),
                        ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                        ('partner_id.total_sale_order_last_12_months', '>', 0),
                    ],
                    order='total_sale_order_last_12_months desc'                
                )
                if len(crm_lead_ids_criterio_2_arelux)>0:
                    crm_lead_id = crm_lead_ids_criterio_2_arelux[0]            
            #criterio_3
            if crm_lead_id==False:
                #criterio_3 (Todocesped)
                crm_lead_ids_criterio_3_todocesped = self.env['crm.lead'].search(
                    [
                        ('id', 'in', crm_lead_ids.ids),
                        ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                        ('partner_id.total_sale_order_last_12_months', '>', 0),
                        ('ar_qt_todocesped_pf_customer_type', 'in', ('construction','architect','decorator','event_planner'))
                    ], 
                    order='total_sale_order_last_12_months desc'
                )
                if len(crm_lead_ids_criterio_3_todocesped)>0:
                    crm_lead_id = crm_lead_ids_criterio_3_todocesped[0]
                #criterio_3 (Arelux)
                crm_lead_ids_criterio_3_arelux = self.env['crm.lead'].search(
                    [
                        ('id', 'in', crm_lead_ids.ids),
                        ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                        ('partner_id.total_sale_order_last_12_months', '>', 0),
                    ], 
                    order='total_sale_order_last_12_months desc'
                )
                if len(crm_lead_ids_criterio_3_arelux)>0:
                    crm_lead_id = crm_lead_ids_criterio_3_arelux[0]                
            #other
            if crm_lead_id==False:
                crm_lead_ids_criterio_other = self.env['crm.lead'].search([('id', 'in', crm_lead_ids.ids)])
                if len(crm_lead_ids_criterio_other)>0:
                    crm_lead_id = crm_lead_ids_criterio_other[0] 
            #operations
            if crm_lead_id!=False:
                crm_lead_id.date_action = current_date.strftime("%Y-%m-%d %H:%M:%S")
                
                response['errors'] = False                                   
                #raise Warning("Asignada fecha de siguiente actividad al flujo dormido mas prioritario")
            else:
                #raise Warning("No tienes flujos de objetivo 'Despertar' sin siguiente actividad para poder asignarte")
                response['error'] = "No tienes flujos de objetivo Despertar sin siguiente actividad para poder asignarte"                 
        #return
        return response                                                                                                    
    
    @api.multi    
    def cron_odoo_crm_lead_change_inactivos(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_inactivos')
        self.cron_odoo_crm_lead_change_inactivos_todocesped()#Todocesped
        self.cron_odoo_crm_lead_change_inactivos_arelux()#Arelux
                
    @api.multi    
    def cron_odoo_crm_lead_change_inactivos_todocesped(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_inactivos_todocesped')
        #search    
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'activation')),
                ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.ar_qt_todocesped_pf_customer_type', '!=', False),
                ('partner_id.ar_qt_todocesped_pf_customer_type', '!=', 'other'),                    
                ('partner_id.total_sale_order', '=', 0),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )
        #activation
        crm_activity_objective_ids_activation = self.env['crm.activity.objective'].search([('objective_type', '=', 'activation')])
        if len(crm_activity_objective_ids_activation)>0:
            crm_activity_objective_id_activation = crm_activity_objective_ids_activation[0]
            if len(crm_lead_ids)>0:
                for crm_lead_id in crm_lead_ids:
                    crm_lead_id.next_activity_objective_id = crm_activity_objective_id_activation.id
                    
    @api.multi    
    def cron_odoo_crm_lead_change_inactivos_arelux(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_crm_lead_change_inactivos_arelux')
        #search    
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', 'not in', ('reserved', 'review', 'closing', 'activation')),
                ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                ('partner_id.ar_qt_customer_type', '=', 'profesional'),
                ('partner_id.ar_qt_arelux_pf_customer_type', '!=', False),
                ('partner_id.ar_qt_arelux_pf_customer_type', '!=', 'other'),                    
                ('partner_id.total_sale_order', '=', 0),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )
        #activation
        crm_activity_objective_ids_activation = self.env['crm.activity.objective'].search([('objective_type', '=', 'activation')])
        if len(crm_activity_objective_ids_activation)>0:
            crm_activity_objective_id_activation = crm_activity_objective_ids_activation[0]
            if len(crm_lead_ids)>0:
                for crm_lead_id in crm_lead_ids:
                    crm_lead_id.next_activity_objective_id = crm_activity_objective_id_activation.id                           
    
    @api.model                        
    def action_boton_pedir_activo(self):
        current_date = datetime.now(pytz.timezone('Europe/Madrid'))
        current_date + relativedelta(hours=2)
        
        response = {
            'errors': True,
            'error': "No tienes flujos de objetivo Activar sin siguiente actividad para poder asignarte"
        }
        
        crm_lead_ids = self.env['crm.lead'].search(
            [
                ('next_activity_objective_id.objective_type', '=', 'activation'),
                ('user_id', '=', self._uid),
                ('date_action', '=', False),
                ('type', '=', 'opportunity'),
                ('active', '=', True),
                ('probability', '>', 0),
                ('probability', '<', 100)
            ]
        )
        if len(crm_lead_ids)>0:
            crm_lead_id = False
            #criterio_1 (Todocesped)            
            crm_lead_ids_criterio_1_todocesped = self.env['crm.lead'].search(
                [
                    ('id', 'in', crm_lead_ids.ids),
                    ('partner_id.ar_qt_activity_type', 'in', ('todocesped', 'both')),
                    ('partner_id.total_sale_order_last_12_months', '>', 0),
                    ('partner_id.ar_qt_todocesped_pf_customer_type', '=', 'other')
                ],
                order='total_sale_order_last_12_months desc'
            )
            if len(crm_lead_ids_criterio_1_todocesped)>0:
                crm_lead_id = crm_lead_ids_criterio_1_todocesped[0]                                                
            #criterio_1 (Arelux)            
            crm_lead_ids_criterio_1_arelux = self.env['crm.lead'].search(
                [
                    ('id', 'in', crm_lead_ids.ids),
                    ('partner_id.ar_qt_activity_type', '=', 'arelux'),
                    ('partner_id.total_sale_order_last_12_months', '>', 0),
                    ('partner_id.ar_qt_arelux_pf_customer_type', '=', 'other')
                ],
                order='total_sale_order_last_12_months desc'
            )
            if len(crm_lead_ids_criterio_1_arelux)>0:
                crm_lead_id = crm_lead_ids_criterio_1_arelux[0]
            #criterio_2 (Todocesped + Arelux)
            if crm_lead_id==False:            
                crm_lead_ids_criterio_2 = self.env['crm.lead'].search(
                    [
                        ('id', 'in', crm_lead_ids.ids),
                        ('partner_id.total_sale_order', '>', 0),
                        ('account_invoice_amount_untaxed_total', '>', 2000)
                    ],
                    order='create_date asc'
                )
                if len(crm_lead_ids_criterio_2)>0:
                    crm_lead_id = crm_lead_ids_criterio_2[0]
            #criterio_3 (Todocesped + Arelux)
            if crm_lead_id==False:            
                crm_lead_ids_criterio_3 = self.env['crm.lead'].search(
                    [
                        ('id', 'in', crm_lead_ids.ids),
                        ('account_invoice_amount_untaxed_total', '>', 0)
                    ],
                    order='create_date asc'
                )
                if len(crm_lead_ids_criterio_3)>0:
                    crm_lead_id = crm_lead_ids_criterio_3[0]
            #other
            if crm_lead_id==False:
                crm_lead_ids_criterio_other = self.env['crm.lead'].search([('id', 'in', crm_lead_ids.ids)])
                if len(crm_lead_ids_criterio_other)>0:
                    crm_lead_id = crm_lead_ids_criterio_other[0] 
            #operations
            if crm_lead_id!=False:
                crm_lead_id.date_action = current_date.strftime("%Y-%m-%d %H:%M:%S")
                
                response['errors'] = False
            else:
                #raise Warning("No tienes flujos de objetivo 'Activar' sin siguiente actividad para poder asignarte")
                response['error'] = "No tienes flujos de objetivo Activar sin siguiente actividad para poder asignarte"                 
        #return
        return response                                                        