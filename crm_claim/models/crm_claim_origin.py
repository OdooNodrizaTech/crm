# -*- coding: utf-8 -*-
from odoo import fields, models

class CrmClaimOrigin(models.Model):
    _name = "crm.claim.origin"
    _description = "Origen de la reclamacion"

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
    )
    other = fields.Boolean(
        string="Otro"
    )    
