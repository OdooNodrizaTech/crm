# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class CrmActivityReport(models.Model):
    _inherit = 'crm.activity.report'

    duration = fields.Float(help='Duracion en minutos y segundos')
    activity_objective_id = fields.Many2one(
        comodel_name='crm.activity.objective',
        string='Objetivo de actividad'
    )
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_activity_report')
        self._cr.execute("""
            CREATE VIEW crm_activity_report AS (
                SELECT m.id,
                m.subtype_id,
                m.activity_objective_id,
                m.author_id,
                m.date,
                m.duration,
                l.id AS lead_id,
                so.id AS order_id,
                l.user_id,
                l.team_id,
                l.country_id,
                l.company_id,
                l.stage_id,
                l.partner_id,
                l.type AS lead_type,
                l.active,
                l.probability
               FROM (
            		mail_message_little m     
            		LEFT JOIN crm_lead cl ON (((m.model)::text = 'crm.lead'::text) AND m.res_id = cl.id)
            		LEFT JOIN sale_order so ON (((m.model)::text = 'sale.order'::text) AND m.res_id = so.id)
            		LEFT JOIN crm_lead l ON (cl.id = l.id OR so.opportunity_id = l.id)
            	)
            	WHERE (
            		(m.model)::text = 'crm.lead'::text
            	) OR (
            		((m.model)::text = 'sale.order'::TEXT)
            		AND so.opportunity_id IS NOT NULL
            	)
            )""")       