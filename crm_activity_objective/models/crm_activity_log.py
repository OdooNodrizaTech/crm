# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class CrmActivityLog(models.TransientModel):
    _inherit = 'crm.activity.log'

    activity_objective_id = fields.Many2one(
        comodel_name='crm.activity.objective',
        string='Objetivo de actividad'
    )    
    duration = fields.Float(
        string='Duracion'
    )
    date_action = fields.Datetime(
        string='Fecha accion'
    )
    date_action_override = fields.Datetime(
        string='Fecha', 
        store=False,
        default=fields.Datetime.now
    )
    
    @api.onchange('lead_id')
    def onchange_lead_id(self):
        super(CrmActivityLog, self).onchange_lead_id()#Fix super
        self.activity_objective_id = self.lead_id.next_activity_objective_id
    
    @api.model
    def create(self, values):
        if values.get('date_action_override'):
            values['date_action'] = values.get('date_action_override')
        #super            
        return super(CrmActivityLog, self).create(values)
            
    @api.multi
    def action_log(self):
        for log in self:
            body_html = "<div><b>%(title)s</b>: %(next_activity)s</div>%(description)s%(note)s" % {
                'title': 'Actividad realizada',
                'next_activity': log.next_activity_id.name,
                'description': log.title_action and '<p><em>%s</em></p>' % log.title_action or '',
                'note': log.note or '',
            }
            log.lead_id.message_post(body_html, 
                subject=log.title_action, 
                subtype_id=log.next_activity_id.subtype_id.id, 
                date=log.date_action,
                activity_objective_id=log.activity_objective_id.id, 
                duration=log.duration
            )
            log.lead_id.write({
                'date_deadline': log.date_deadline,
                'planned_revenue': log.planned_revenue,
                'title_action': False,
                'date_action': False,
                'next_activity_id': False,
            })
        return True            