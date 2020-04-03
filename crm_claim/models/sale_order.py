# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from openerp import api, models, fields
from openerp.exceptions import Warning
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'
                        
    claim = fields.Boolean( 
        string='Es una reposicion'
    )
    claim_id = fields.Many2one(
        comodel_name='crm.claim', 
        string='Reclamacion'
    )    
    
    @api.onchange('claim_id')
    def change_claim_id(self):
        if self.claim_id.id>0 and self.partner_id.id==0:
            self.partner_id = self.claim_id.partner_id