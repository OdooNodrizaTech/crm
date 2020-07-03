# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Crm Activity Objective',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base','crm','mail', 'web'],
    'data': [
        'data/ir_cron.xml',
        'views/crm_activity_log_views.xml',
        'views/crm_activity_report_view.xml',
        'views/crm_activity_objective_views.xml',
        'views/crm_lead.xml',
        'views/template.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': ['static/src/xml/buttons.xml'],
    'installable': True,
    'auto_install': False,    
}