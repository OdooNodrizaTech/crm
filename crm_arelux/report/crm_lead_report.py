# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class CrmLeadReport(models.Model):
    _name = 'crm.lead.report'
    _auto = False
    _description = "Crm Lead Report"
    _rec_name = 'id'

    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency'
    )
    lead_id = fields.Many2one(
        'crm.lead', 
        string='Lead Id',
        readonly=True
    )
    last_date_order_management = fields.Datetime('Date', readonly=True)    
    total_sale_order_last_30_days = fields.Integer('Amount Untaxed Last 30 days', readonly=True)
    total_sale_order_last_90_days = fields.Integer('Amount Untaxed Last 90 days', readonly=True)
    total_sale_order_last_12_months = fields.Integer('Amount Untaxed Last 12 months', readonly=True)
    total_sale_order = fields.Integer('Total Sale Order More Than 300', readonly=True)    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_lead_report')
        self._cr.execute("""
            CREATE VIEW crm_lead_report AS (
                SELECT cl.id, 
                cl.id AS lead_id,
                cl.currency_id,
                MAX(so.orders_date_order_management)::date AS last_date_order_management,
                max(COALESCE(so_last_30_days.orders_number, 0)) AS total_sale_order_last_30_days,
                max(COALESCE(so_last_90_days.orders_number, 0)) AS total_sale_order_last_90_days,
                max(COALESCE(so_last_12_months.orders_number, 0)) AS total_sale_order_last_12_months,
                max(COALESCE(so_more_than_300.orders_number, 0)) AS total_sale_order
                FROM crm_lead AS cl
                LEFT JOIN (
                	SELECT opportunity_id, MAX(date_order_management) AS orders_date_order_management
                	FROM sale_order
                	WHERE claim = FALSE 
                 	AND date_order_management IS NOT NULL 
                  	AND amount_total > 0
                  	AND STATE IN ('sale', 'done')
                	GROUP BY opportunity_id
                ) AS so ON so.opportunity_id = cl.id
                LEFT JOIN (
                	SELECT opportunity_id, count(id) AS orders_number
                	FROM sale_order
                	WHERE claim = FALSE 
                 	AND confirmation_date BETWEEN (NOW()::date - INTERVAL '30' DAY)::date AND NOW()::DATE
                  	AND amount_untaxed > 300
                  	AND STATE IN ('sale', 'done')
                	GROUP BY opportunity_id
                ) AS so_last_30_days ON so_last_30_days.opportunity_id = cl.id
                LEFT JOIN (
                	SELECT opportunity_id, count(id) AS orders_number
                	FROM sale_order
                	WHERE claim = FALSE 
                 	AND confirmation_date BETWEEN (NOW()::date - INTERVAL '90' DAY)::date AND NOW()::DATE
                  	AND amount_untaxed > 300
                  	AND STATE IN ('sale', 'done')
                	GROUP BY opportunity_id
                ) AS so_last_90_days ON so_last_90_days.opportunity_id = cl.id
                LEFT JOIN (
                	SELECT opportunity_id, count(id) AS orders_number
                	FROM sale_order
                	WHERE claim = FALSE 
                 	AND confirmation_date BETWEEN (NOW()::date - INTERVAL '12' MONTH)::date AND NOW()::DATE
                  	AND amount_untaxed > 300
                  	AND STATE IN ('sale', 'done')
                	GROUP BY opportunity_id
                ) AS so_last_12_months ON so_last_12_months.opportunity_id = cl.id
                LEFT JOIN (
                	SELECT opportunity_id, count(id) AS orders_number
                	FROM sale_order
                	WHERE claim = FALSE 
                  	AND amount_untaxed > 300
                  	AND STATE IN ('sale', 'done')
                	GROUP BY opportunity_id
                ) AS so_more_than_300 ON so_more_than_300.opportunity_id = cl.id
                WHERE cl.TYPE = 'opportunity'
                GROUP BY cl.id
                ORDER BY last_date_order_management DESC
            )""")       