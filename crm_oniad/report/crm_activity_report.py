# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class CrmActivityReport(models.Model):
    _inherit = 'crm.activity.report'

    duration = fields.Float(help='Duracion en minutos y segundos')
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_activity_report')
        self._cr.execute("""
            CREATE VIEW crm_activity_report AS (
                select
                    m.id,
                    m.subtype_id,
                    m.author_id,
                    m.date,
                    m.subject,
                    m.duration,
                    l.id as lead_id,
                    l.user_id,
                    l.team_id,
                    l.country_id,
                    l.company_id,
                    l.stage_id,
                    l.partner_id,
                    l.type as lead_type,
                    l.active,
                    l.probability
                from
                    "mail_message" m
                join
                    "crm_lead" l
                on
                    (m.res_id = l.id)
                WHERE
                    (m.model = 'crm.lead')
            )""")       