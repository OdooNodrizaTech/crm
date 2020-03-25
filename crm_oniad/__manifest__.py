# -*- coding: utf-8 -*-
{
    'name': 'Crm OniAd',
    'version': '10.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT)',
    'website': 'https://nodrizatech.com/',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': ['base', 'crm'],
    'data': [
        'data/crm_lead_source_data.xml',
        'views/crm_activity_log_views.xml',
        'views/crm_activity_report_view.xml',
        'views/crm_lead_view.xml',
    ],
    'installable': True,
    'auto_install': False,    
}