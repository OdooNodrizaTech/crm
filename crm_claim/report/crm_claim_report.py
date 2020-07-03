# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, tools

import logging
_logger = logging.getLogger(__name__)

class CrmClaimReport(models.AbstractModel):
    _name = 'report.crm_claim.pdf'
    _description = 'Crm Claim Report'
    
    code = fields.Char(
        string='Numero',
        readonly=True
    )        
    description = fields.Text(readonly=True)
    resolution = fields.Text(readonly=True)
    date_closed = fields.Datetime(
        string='Fecha cierre',
        readonly=True
    )
    date = fields.Datetime(
        string='Fecha',
        readonly=True
    )
    categ_id = fields.Many2one(
        comodel_name='crm.claim.category',
        string='Tipo de reclamacion',
        readonly=True
    )
    org_id = fields.Many2one(
        comodel_name='crm.claim.origin',
        string='Origen',
        readonly=True
    )
    corrective_action = fields.Boolean(
        string="Necesita accion correctiva",
        readonly=True
    )    
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
        readonly=True
    )        
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contacto',
        readonly=True
    )   
    stage_id = fields.Many2one(
        comodel_name='crm.claim.stage',
        string='Etapa',
        readonly=True
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment", 
        inverse_name="res_id", 
        compute="_add_attachment",
        readonly=True
    )
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_claim_report')
        self._cr.execute("""
            CREATE VIEW crm_claim_report AS (
                SELECT
                min(c.id) AS id,
                c.code,
                c.description,
                c.resolution,
                c.date AS date,
                c.date_closed,
                c.corrective_action,
                c.user_id,
                c.stage_id,
                c.partner_id,
                c.org_id,
                c.categ_id,
                avg(extract('epoch' FROM (c.date_closed-c.create_date)))/(3600*24) AS delay_close,
                (
                    SELECT count(id)
                    FROM mail_message
                    WHERE model='crm.claim'
                    AND res_id=c.id
                ) AS email
                FROM crm_claim AS c
                GROUP BY c.id, c.code, c.date, c.date_closed, c.corrective_action, c.user_id, c.stage_id, c.partner_id, c.org_id, c.categ_id
            )""")    
        
    @api.multi
    def _add_attachment(self):
        self.attachment_ids = self.env['ir.attachment'].search([('res_model','=','crm.claim'),('res_id','=',self.id)])
        if self.attachment_ids!=False:
            for attachment_id in self.attachment_ids:                
                attachment_id.url = '/web/image/'+str(attachment_id.id)                       