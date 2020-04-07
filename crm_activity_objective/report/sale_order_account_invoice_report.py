# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class SaleOrderAccountInvoiceReport(models.Model):
    _name = 'sale.order.account.invoice.report'
    _auto = False
    _description = "Sale Order Account Invoice Report"
    _rec_name = 'id'
    
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        readonly=True
    )
    order_id = fields.Many2one(
        'sale.order', 
        string='Sale Order',
        readonly=True
    )
    invoice_id = fields.Many2one(
        'account.invoice', 
        string='Account Invoice',
        readonly=True
    )
    opportunity_id = fields.Many2one(
        'crm.lead', 
        string='Opportunity id',
        readonly=True
    )
    type = fields.Char('Type', readonly=True)
    date_invoice = fields.Date('Date Invoice', readonly=True)
    amount_untaxed = fields.Monetary('Amount Untaxed', readonly=True)
    margin = fields.Monetary('Margin', readonly=True)    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'sale_order_account_invoice_report')
        self._cr.execute("""
            CREATE VIEW sale_order_account_invoice_report AS (
                SELECT so.id,                                
                ai.currency_id,
                so.id AS order_id,
                ail.invoice_id, 
                so.opportunity_id, 
                ai.type, 
                ai.date_invoice, 
                ai.amount_untaxed::float,
                ai.margin::float
                FROM sale_order_line_invoice_rel AS solir
                LEFT JOIN account_invoice_line AS ail ON solir.invoice_line_id = ail.id
                LEFT JOIN account_invoice AS ai ON ail.invoice_id = ai.id
                LEFT JOIN sale_order_line AS sol ON solir.order_line_id = sol.id
                LEFT JOIN sale_order AS so ON sol.order_id = so.id
                WHERE so.opportunity_id IS NOT NULL
                GROUP BY so.id, ail.invoice_id, ai.currency_id, ai.TYPE, ai.date_invoice, ai.amount_untaxed, ai.margin
                ORDER BY so.opportunity_id ASC
            )""")