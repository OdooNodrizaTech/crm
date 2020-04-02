# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class ResPartnerAccountInvoiceReport(models.Model):
    _name = 'res.partner.account.invoice.report'
    _auto = False
    _description = "Res Partner Account Invoice Report"
    _rec_name = 'id'

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Res Partner',
        readonly=True
    )
    amount_untaxed_total_out_invoice = fields.Monetary('Amount Untaxed Total Out Invoice', readonly=True)
    amount_untaxed_total_out_refund = fields.Monetary('Amount Untaxed Total Out Refund', readonly=True)
    margin_total_out_invoice = fields.Monetary('Margin Total Out Invoice', readonly=True)
    margin_total_out_refund = fields.Monetary('Margin Total Out Refund', readonly=True)    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'res_partner_account_invoice_report')
        self._cr.execute("""
            CREATE VIEW res_partner_account_invoice_report AS (
                SELECT ai_total.partner_id AS id,
                ai_total.currency_id,
                ai_total.partner_id AS partner_id,                 
                CASE WHEN sum(ai_total.amount_untaxed) IS NULL THEN 0 ELSE sum(ai_total.amount_untaxed) END AS amount_untaxed_total_out_invoice,
                CASE WHEN sum(ai_refund_total.amount_untaxed) IS NULL THEN 0 ELSE sum(ai_refund_total.amount_untaxed) END AS amount_untaxed_total_out_refund,
                CASE WHEN sum(ai_total.margin) IS NULL THEN 0 ELSE sum(ai_total.margin) END AS margin_total_out_invoice,
                CASE WHEN sum(ai_refund_total.margin) IS NULL THEN 0 ELSE sum(ai_refund_total.margin) END AS margin_total_out_refund
                FROM account_invoice AS ai_total
                LEFT JOIN account_invoice AS ai_refund_total ON (ai_refund_total.partner_id = ai_total.partner_id AND ai_refund_total.TYPE = 'out_refund' AND ai_refund_total.STATE IN ('open', 'paid'))
                WHERE ai_total.TYPE = 'out_invoice' AND ai_total.STATE IN ('open', 'paid')                                        
                GROUP BY ai_total.partner_id, ai_total.currency_id
                ORDER BY id ASC
            )""")