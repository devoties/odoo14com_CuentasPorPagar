# -*- coding:utf-8 -*-

from odoo import fields, models, api


class ExtensionCuentasbancarias(models.Model):

    _inherit = 'res.partner.bank'

    es_caratura_estado_cuenta = fields.Boolean(string='¿CEC?')

    caratula_estado_cuenta = fields.Binary(string='Archivo Caratula de estado de cuenta')

    caratula_estado_cuenta_filename = fields.Char(string='Nombre del archivo')

    check = fields.Boolean(string='¿Es cuenta default?')