# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class ResPartnerMailMessageReport(models.Model):
    _name = 'res.partner.mail.message.report'
    _auto = False
    _description = "Res Partner Mail Message Report"
    _rec_name = 'id'

    partner_id = fields.Many2one(
        'res.partner', 
        string='Res Partner',
        readonly=True
    )
    full_date = fields.Datetime('Full date', readonly=True)
    date = fields.Date('Date', readonly=True)    
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'res_partner_mail_message_report')
        self._cr.execute("""
            CREATE VIEW res_partner_mail_message_report AS (
                SELECT mmrpr.res_partner_id AS id, 
                mmrpr.res_partner_id AS partner_id,
                MAX(mm.DATE) AS full_date, 
                MAX(mm.DATE)::date AS date
                FROM mail_message_res_partner_rel AS mmrpr
                LEFT JOIN mail_message_little AS mm ON mmrpr.mail_message_id = mm.mail_message_id
                WHERE mm.subtype_id IN (1,2,4)
                GROUP BY mmrpr.res_partner_id
                ORDER BY id ASC
            )""")