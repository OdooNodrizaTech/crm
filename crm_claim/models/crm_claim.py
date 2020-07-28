# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CrmClaim(models.Model):
    _name = "crm.claim"
    _description = "Crm claims"
    _order = "date desc"
    _inherit = ['mail.thread']
    _rec_name = 'code'

    code = fields.Char(
        string='Number',
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )
    active = fields.Boolean(
        default=True,
    )
    description = fields.Text()
    resolution = fields.Text()
    quality_observations = fields.Text()
    date_closed = fields.Datetime(
        string='Date closed'
    )
    date = fields.Datetime(
        string='Date',
        index=True,
        default=fields.Datetime.now
    )
    categ_id = fields.Many2one(
        comodel_name='crm.claim.category',
        string='Categ id'
    )
    model_ref_id = fields.Reference(
        selection=[
            ('sale.order', 'Pedido de venta'),
            ('res.partner', 'Empresa'),
            ('account.invoice', 'Factura'),
            ('product.product', 'Producto')
        ],
        string='Ref'
    )
    reference = fields.Char(
        string='Ref (name)',
        help='Auto-define ref with model_ref_id'
    )
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Carrier id',
        store=True
    )
    org_id = fields.Many2one(
        comodel_name='crm.claim.origin',
        string='Origin',
    )
    org_other_show = fields.Boolean(
        compute='_compute_org_other_show',
        store=False
    )
    org_other = fields.Char(
        string='Other',
    )
    corrective_action = fields.Boolean(
        string="Corrective action is need?"
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User id',
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    stage_id = fields.Many2one(
        comodel_name='crm.claim.stage',
        string='Stage',
        track_visibility='onchange',
        default=1,
    )
    order_id = fields.Many2one(
        comodel_name='sale.order',
        compute='_compute_order_id',
        string='Order'
    )
    _sql_constraints = [
        ('crm_claim_unique_code', 'UNIQUE (code)',
         'The code must be unique'),
    ]

    @api.onchange('org_id')
    def change_org_id(self):
        self._get_org_other_show()

    def _compute_order_id(self):
        if self.id:
            items = self.env['sale.order'].search(
                [                
                    ('claim', '=', True),
                    ('claim_id', '=', self.id)
                 ])
            if items:
                for item in items:
                    self.order_id = item.id

    def _compute_org_other_show(self):
        self.org_other_show = False
        if self.org_id.id and self.org_id.other:
            self.org_other_show = True

    @api.onchange('model_ref_id')
    def change_model_ref_id(self):
        self.carrier_id = False
        if self.model_ref_id:
            if self.model_ref_id._name == 'sale.order':
                if self.model_ref_id:
                   if self.model_ref_id.carrier_id:
                        self.carrier_id = self.model_ref_id.carrier_id.id

    @api.model
    def create(self, values):
        # code
        if values.get('code', '/') == '/':
            values['code'] = self.env['ir.sequence'].next_by_code('crm.claim')
        # model_ref_id
        if 'model_ref_id' in values and values.get('model_ref_id'):
            model_ref_name, model_ref_id = values.get('model_ref_id').split(',')
            # model_ref_search_id
            model_ref_search_id = self.env[model_ref_name].search(
                [
                    ('id', '=', model_ref_id)
                ]
            )[0]
            # partner_id
            if model_ref_name == 'res.partner':
                values['partner_id'] = model_ref_search_id.id
            else:
                values['partner_id'] = model_ref_search_id.partner_id.id
            # reference
            if model_ref_name != 'account.invoice':
                values['reference'] = model_ref_search_id.name
            else:
                values['reference'] = model_ref_search_id.number
        # return
        return super(CrmClaim, self).create(values)

    @api.multi
    def write(self, values):
        # date_closed
        if values.get('resolution') and not self.date_closed:
            values['date_closed'] = fields.datetime.now()
        # model_ref_id
        if 'model_ref_id' in values and values.get('model_ref_id') :
            model_ref_name, model_ref_id = values.get('model_ref_id').split(',')
            # model_ref_search_id
            model_ref_search_id = self.env[model_ref_name].search(
                [
                    ('id', '=', model_ref_id)
                ]
            )[0]
            # partner_id
            if model_ref_name == 'res.partner':
                values['partner_id'] = model_ref_search_id.id
            else:
                values['partner_id'] = model_ref_search_id.partner_id.id
            # reference
            if model_ref_name != 'account.invoice':
                values['reference'] = model_ref_search_id.name
            else:
                values['reference'] = model_ref_search_id.number
        # return
        return super(CrmClaim, self).write(values)
