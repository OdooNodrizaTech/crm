# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class CrmLeadSource(models.Model):
    _name = 'crm.lead.source'
    _description = 'Crm Lead Source'
    _order = "position asc"    
    
    name = fields.Char(        
        string='Name'
    )
    position = fields.Integer(        
        string='Position'
    )                                       