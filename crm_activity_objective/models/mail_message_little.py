# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class MailMessageLittle(models.Model):
    _name = 'mail.message.little'
    _description = 'Mail Message Little'
    
    mail_message_id = fields.Many2one(
        comodel_name='mail.message',
        string='Mail Message',
        ondelete='cascade'
    )
    parent_id = fields.Integer(        
        string='Parent Id'
    )
    date = fields.Datetime('Fecha')
    model = fields.Char('Modelo')
    res_id = fields.Integer('Res Od')
    message_type = fields.Selection([
        ('email', 'Email'),
        ('comment', 'Comment'),
        ('notification', 'System notification')],
        'Type', default='email'
    )
    subtype_id = fields.Many2one(
        comodel_name='mail.message.subtype',
        string='Subtipo'
    )
    author_id = fields.Many2one(
        comodel_name='res.partner',
        string='Author'
    )    
    duration = fields.Float(help='Duracion en minutos y segundos')
    activity_objective_id = fields.Many2one(
        comodel_name='crm.activity.objective',
        string='Objetivo de actividad'
    )