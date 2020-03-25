# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class CrmLeadSource(models.Model):
    _name = 'crm.lead.source'
    _description = 'Crm Lead Source'
    _order = "position asc"    
    
    name = fields.Char(        
        string='Nombre'
    )
    position = fields.Integer(        
        string='Posicion'
    )                                       