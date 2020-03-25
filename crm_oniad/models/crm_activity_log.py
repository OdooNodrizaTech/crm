# -*- coding: utf-8 -*-
from odoo import api, fields, models
from openerp.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class CrmActivityLog(models.TransientModel):
    _inherit = 'crm.activity.log'

    duration = fields.Float(
        string='Duracion'
    )
    date_action_override = fields.Date(
        string='Fecha', 
        store=False,
        default=fields.Datetime.now
    )
    
    @api.model
    def create(self, values):
        allow_create = True
        if values.get('date_action_override')==False:
            allow_create = False
            raise Warning("No se puede guardar una actividad sin fecha")
        else:        
            values['date_action'] = values.get('date_action_override')
        
        if allow_create==True:                    
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
            log.lead_id.message_post(body_html, subject=log.title_action, subtype_id=log.next_activity_id.subtype_id.id, date=log.date_action, duration=log.duration)
            log.lead_id.write({
                'date_deadline': log.date_deadline,
                'planned_revenue': log.planned_revenue,
                'title_action': False,
                'date_action': False,
                'next_activity_id': False,
            })
        return True            