# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmClaimStage(models.Model):
    _name = "crm.claim.stage"
    _description = "Crm claim stage"
    _order = "sequence"

    name = fields.Char(
        string='Name',
        required=True,
        translate=True
    )
    sequence = fields.Integer(
        default=1,
        help="Use to sort stages",
    )
    case_default = fields.Boolean(
        string='Default to all team',
        help="If you check this field, this stage will be proposed by default "
             "on each sales team. It will not assign this stage to existing "
             "teams."
    )
