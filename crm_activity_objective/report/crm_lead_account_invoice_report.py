# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class CrmLeadAccountInvoiceReport(models.Model):
    _name = 'crm.lead.account.invoice.report'
    _auto = False
    _description = "Crm Lead Account Invoice Report"
    _rec_name = 'id'

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        readonly=True
    )
    lead_id = fields.Many2one(
        'crm.lead', 
        string='Lead Id',
        readonly=True
    )
    amount_untaxed_total_out_invoice = fields.Monetary('Amount Untaxed Total Out Invoice', readonly=True)
    amount_untaxed_total_out_refund = fields.Monetary('Amount Untaxed Total Out Refund', readonly=True)
    margin_total_out_invoice = fields.Monetary('Margin Total Out Invoice', readonly=True)
    margin_total_out_refund = fields.Monetary('Margin Total Out Refund', readonly=True)        
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_lead_account_invoice_report')
        self._cr.execute("""
            CREATE VIEW crm_lead_account_invoice_report AS (
                SELECT cl.id,                 
                soair_total.currency_id,
                cl.id AS lead_id,
                sum(COALESCE(soair_total.amount_untaxed, 0)) AS amount_untaxed_total_out_invoice,
                sum(COALESCE(soair_total_refund.amount_untaxed, 0)) AS amount_untaxed_total_out_refund,
                sum(COALESCE(soair_total.margin, 0)) AS margin_total_out_invoice,
                sum(COALESCE(soair_total_refund.margin, 0)) AS margin_total_out_refund                
                FROM crm_lead AS cl
                LEFT JOIN sale_order_account_invoice_report AS soair_total ON (soair_total.opportunity_id = cl.id AND soair_total.TYPE = 'out_invoice')
                LEFT JOIN sale_order_account_invoice_report AS soair_total_refund ON (soair_total_refund.opportunity_id = cl.id AND soair_total_refund.type = 'out_refund')
                WHERE cl.type = 'opportunity'
                GROUP BY cl.id, soair_total.currency_id
                ORDER BY cl.id ASC
            )""")