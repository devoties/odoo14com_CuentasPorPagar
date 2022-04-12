# -*- coding:utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

class IneSat(models.Model):
    _name = 'ine_sat'

    name = fields.Char(string='Nombre INE',default='INE')

    ine = fields.Binary(string='Archivo de INE')

    ine_filename = fields.Char(string='Nombre de archivo')

    ine_partner_rel = fields.Many2one(string='',comodel_name='res.partner')

    fecha_vencimiento = fields.Date(string='Fecha Vencimiento')


