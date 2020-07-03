# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    total_sale_order = fields.Integer(
        string="Nº Pedidos",
        help="Nº pedidos > 300€ de ese cliente",
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
    account_invoice_amount_untaxed_total = fields.Monetary(
        string="Facturacion historico",
        help="Historico de facturacion (BI) de ese cliente",
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
    
    @api.multi    
    def cron_odoo_res_partner_fields_generate(self, cr=None, uid=False, context=None):
        _logger.info('sql_1 (total_sale_order, date_from_last_sale_order)')
        self._cr.execute("""
            UPDATE res_partner SET (total_sale_order, total_sale_order_last_30_days, total_sale_order_last_90_days, total_sale_order_last_12_months, date_from_last_sale_order) = (
            	SELECT rpr.total_sale_order, rpr.total_sale_order_last_30_days, rpr.total_sale_order_last_90_days, rpr.total_sale_order_last_12_months, rpr.last_date_order_management 
            	FROM res_partner_report AS rpr 
            	WHERE rpr.partner_id = res_partner.id
            ) 
            WHERE res_partner.id IN (
            	SELECT rpr2.partner_id 
            	FROM res_partner_report AS rpr2 
            	LEFT JOIN res_partner AS rp ON rpr2.partner_id = rp.id 
            	WHERE (
            		(rpr2.total_sale_order <> rp.total_sale_order)
                    OR (rpr2.total_sale_order_last_30_days <> rp.total_sale_order_last_30_days) 
            		OR (rpr2.total_sale_order_last_90_days <> rp.total_sale_order_last_90_days)
                    OR (rpr2.total_sale_order_last_12_months  <> rp.total_sale_order_last_12_months ) 
            		OR (rp.date_from_last_sale_order IS NOT NULL AND rpr2.last_date_order_management <> rp.date_from_last_sale_order) 
            		OR (rp.date_from_last_sale_order IS NULL AND rpr2.last_date_order_management IS NOT NULL)
            	) 
            	LIMIT 1000
            )
        """)        
        _logger.info('sql_2 (account_invoice_amount_untaxed_total)')
        self._cr.execute("""
            UPDATE res_partner SET (account_invoice_amount_untaxed_total) = (
            	SELECT ROUND((rpair.amount_untaxed_total_out_invoice-rpair.amount_untaxed_total_out_refund)::numeric,2)::FLOAT 
            	FROM res_partner_account_invoice_report AS rpair 
            	WHERE rpair.partner_id = res_partner.id
            ) 
            WHERE res_partner.id IN (
            	SELECT rpair2.partner_id 
                FROM res_partner_account_invoice_report AS rpair2 
                LEFT JOIN res_partner AS rp ON rpair2.partner_id = rp.id 
                WHERE (rpair2.amount_untaxed_total_out_invoice IS NOT NULL OR rpair2.amount_untaxed_total_out_refund IS NOT NULL) 
                AND (
                	(
                	rp.account_invoice_amount_untaxed_total IS NOT NULL
                	AND (ROUND((rpair2.amount_untaxed_total_out_invoice-rpair2.amount_untaxed_total_out_refund)::numeric,2)::float <> rp.account_invoice_amount_untaxed_total)
                	)
                	OR rp.account_invoice_amount_untaxed_total IS NULL
                ) 
            	LIMIT 1000
            )
        """)
        _logger.info('sql_3 (date_from_last_message)')
        self._cr.execute("""
            UPDATE res_partner SET (date_from_last_message) = (
            	SELECT rpmmr.DATE 
            	FROM res_partner_mail_message_report AS rpmmr 
            	WHERE rpmmr.partner_id = res_partner.id
            ) 
            WHERE res_partner.id IN (
            	SELECT rpmmr2.partner_id 
            	FROM res_partner_mail_message_report AS rpmmr2 
            	LEFT JOIN res_partner AS rp ON rpmmr2.partner_id = rp.id 
            	WHERE (
            		(rp.date_from_last_message IS NOT NULL AND rpmmr2.DATE  <> rp.date_from_last_message) 
            		OR (rp.date_from_last_message IS NULL AND rpmmr2.DATE IS NOT NULL)
            	) 
            	LIMIT 1000
            )
        """)
        
    @api.multi    
    def cron_odoo_res_partner_fields_generate_days(self, cr=None, uid=False, context=None):
        _logger.info('cron_odoo_res_partner_fields_generate_days')
        _logger.info('sql_1 (days_from_last_sale_order)')
        self._cr.execute("""
            UPDATE res_partner SET (days_from_last_sale_order) = (
            	SELECT(NOW()::date - rp.date_from_last_sale_order) 
            	FROM res_partner AS rp 
            	WHERE rp.id = res_partner.id
            ) 
            WHERE res_partner.date_from_last_sale_order IS NOT NULL
        """)  
        _logger.info('sql_2 (days_from_last_message)')
        self._cr.execute("""
            UPDATE res_partner SET (days_from_last_message) = (
            	SELECT(NOW()::date - rp.date_from_last_message) 
            	FROM res_partner AS rp 
            	WHERE rp.id = res_partner.id
            ) 
            WHERE res_partner.date_from_last_message IS NOT NULL
        """)