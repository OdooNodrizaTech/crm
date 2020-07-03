# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class ResPartnerReport(models.Model):
    _name = 'res.partner.report'
    _auto = False
    _description = "Res Partner Report"
    _rec_name = 'id'
    
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency'
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Res Partner'
    )
    last_date_order_management = fields.Datetime('Date', readonly=True)    
    total_sale_order_last_30_days = fields.Integer('Amount Untaxed Last 30 days', readonly=True)
    total_sale_order_last_90_days = fields.Integer('Amount Untaxed Last 90 days', readonly=True)
    total_sale_order_last_12_months = fields.Integer('Amount Untaxed Last 12 months', readonly=True)
    total_sale_order = fields.Integer('Total Sale Order More Than 300', readonly=True)    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'res_partner_report')
        self._cr.execute("""
            CREATE VIEW res_partner_report AS (
                SELECT
                rp.id,
                rc.currency_id,
                rp.id as partner_id,
                MAX(so.orders_date_order_management)::date AS last_date_order_management, 
                max(COALESCE(so_last_30_days.orders_number, 0)) AS total_sale_order_last_30_days,
                max(COALESCE(so_last_90_days.orders_number, 0)) AS total_sale_order_last_90_days,
                max(COALESCE(so_last_12_months.orders_number, 0)) AS total_sale_order_last_12_months,
                max(COALESCE(so_more_than_300.orders_number, 0)) AS total_sale_order
                FROM res_partner AS rp
                LEFT JOIN res_company AS rc ON rp.company_id = rc.id
                LEFT JOIN (
                	SELECT partner_invoice_id, MAX(date_order_management) AS orders_date_order_management
                	FROM sale_order
                	WHERE claim = FALSE AND amount_total > 0 AND STATE NOT IN ('draft', 'cancell')
                	GROUP BY partner_invoice_id
                ) AS so ON so.partner_invoice_id = rp.id
                LEFT JOIN (
                	SELECT partner_invoice_id, count(id) orders_number, sum(amount_total) orders_amount
                	FROM sale_order
                	WHERE claim = false AND amount_total > 0 AND STATE in ('sale','done') AND confirmation_date between (now()::date - interval '30' day)::date and now()::date
                	GROUP BY partner_invoice_id
                ) AS so_last_30_days ON so_last_30_days.partner_invoice_id = rp.id
                LEFT JOIN (
                	SELECT partner_invoice_id, count(id) orders_number, sum(amount_total) orders_amount
                	FROM sale_order
                	WHERE claim = false AND amount_total > 0 AND STATE in ('sale', 'done') AND confirmation_date between (now()::date - interval '90' day)::date and now()::date
                	GROUP BY partner_invoice_id
                ) AS so_last_90_days ON so_last_90_days.partner_invoice_id = rp.id
                LEFT JOIN (
                	SELECT partner_invoice_id, count(id) orders_number, sum(amount_total) orders_amount
                	FROM sale_order
                	WHERE claim = false AND amount_total > 0 AND STATE in ('sale', 'done') AND confirmation_date between (now()::date - interval '12' month)::date and now()::date
                	GROUP BY partner_invoice_id
                ) AS so_last_12_months ON so_last_12_months.partner_invoice_id = rp.id
                LEFT JOIN (
                	SELECT partner_invoice_id, count(id) orders_number, sum(amount_total) orders_amount
                	FROM sale_order
                	WHERE claim = FALSE AND amount_untaxed > 300 AND state in ('sale', 'done')
                	GROUP BY partner_invoice_id
                ) AS so_more_than_300 ON so_more_than_300.partner_invoice_id = rp.id
                WHERE rp.active = true AND rp.TYPE = 'contact'
                GROUP BY rp.id, rc.currency_id
                ORDER BY total_sale_order DESC
            )""")       