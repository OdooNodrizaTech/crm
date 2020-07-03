# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Crm Activity Objective Arelux',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['crm_activity_objective'],
    'data': [
        'data/ir_cron.xml',
        'views/crm_lead.xml',
    ],
    'installable': True,
    'auto_install': False,    
}