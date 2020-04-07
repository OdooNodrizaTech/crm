# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class CrmLeadMailMessageReport(models.Model):
    _name = 'crm.lead.mail.message.report'
    _auto = False
    _description = "Crm Lead Mail Message Report"
    _rec_name = 'lead_id'
    
    lead_id = fields.Many2one(
        'crm.lead', 
        string='Lead Id',
        readonly=True
    )
    date = fields.Date('Date', readonly=True)    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_lead_mail_message_report')
        self._cr.execute("""
            CREATE VIEW crm_lead_mail_message_report AS (
                SELECT 
                MAX(mm.DATE) AS full_date, 
                MAX(mm.DATE)::date AS DATE,
                CASE
                WHEN mm.model='sale.order' THEN coalesce((SELECT so.opportunity_id FROM sale_order so WHERE mm.model = 'sale.order' AND so.id = mm.res_id ),0)
                ELSE mm.res_id
                END AS lead_id
                FROM mail_message_little AS mm
                WHERE (mm.subtype_id IN (1,2,4) AND mm.model = 'crm.lead')
                OR (mm.subtype_id IN (1,4) AND mm.model = 'sale.order')
                GROUP BY lead_id
                ORDER BY lead_id DESC                
            )""")