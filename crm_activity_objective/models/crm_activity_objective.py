# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class CrmActivityObjective(models.Model):
    _name = 'crm.activity.objective'
    _description = 'Crm Activity Objetice'
    _order = "probability desc"
    
    name = fields.Char(
        string='Nombre',
    )
    objective_type = fields.Selection(
        selection=[
            ('reserved','Reservado'), 
            ('prospecting','Prospeccion'), 
            ('activation','Activacion'), 
            ('review','Repaso'), 
            ('closing','Cierre'), 
            ('tracking','Seguimiento'), 
            ('wake','Despertar')
        ],
        string='Tipo'
    )
    crm_activity_ids = fields.Many2many(
        'crm.activity', 'crm_activity_objective_rel', 'activity_id', 'activity_objective_id',
        string='Actividades'
    )
    probability = fields.Integer(
        string='Probabilidad', 
        default=0
    )