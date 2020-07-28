# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmClaimCategory(models.Model):
    _name = "crm.claim.category"
    _description = "Crm claim category"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
