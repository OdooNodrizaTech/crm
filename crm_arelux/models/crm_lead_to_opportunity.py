# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
_logger = logging.getLogger(__name__)

from openerp import api, models, fields
from openerp.exceptions import Warning

class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    
    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id!=False:
            team_id_old = self.team_id
            super(Lead2OpportunityPartner, self)._onchange_user()
            self.team_id = team_id_old#prevent auto-change team_id