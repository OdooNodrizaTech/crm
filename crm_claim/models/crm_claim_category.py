# -*- coding: utf-8 -*-
from odoo import fields, models

class CrmClaimCategory(models.Model):
    _name = "crm.claim.category"
    _description = "Categoria de reclamaciones"

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )    
