# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

class CrmClaimCategory(models.Model):
    _name = "crm.claim.category"
    _description = "Categoria de reclamaciones"

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )    
