# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Claims",
    "version": "12.0.1.0.0",
    "author": "Odoo Nodriza Tech (ONT)",
    "website": "https://nodrizatech.com/",
    "category": "Tools",
    "license": "AGPL-3",
    "depends": [
        "base",
        "crm",
        "sale",
        "delivery"
    ],
    "data": [
        "views/crm_claim_view.xml",
        "views/crm_claim_category_view.xml",
        "views/crm_claim_origin_view.xml",
        "views/crm_claim_stage_view.xml",
        "views/res_partner_view.xml",
        "views/crm_claim_views.xml",
        "views/sale_order_view.xml",
        "security/ir.model.access.csv",
        "report/report_crm_claim_report.xml",
        "data/crm_claim_data.xml",
        "data/claim_sequence.xml",
    ],
    "installable": True,
}