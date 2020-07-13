# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmClaimOrigin(models.Model):
    _name = "crm.claim.origin"
    _description = "Crm claim origin"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    other = fields.Boolean(
        string="Other"
    )    
