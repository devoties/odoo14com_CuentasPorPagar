# -*- coding:utf-8 -*-how save many2many custom more data

from odoo import fields, models, api

class LotesCfdi(models.Model):

    _inherit = 'account.payment'

    complemento_de_pago_file = fields.Binary(string='Complemento de pago')

    complemento_de_pago_filename = fields.Char(string='Nombre de archivo')

    comprobante_pago_file = fields.Binary(string='Comprobante de pago')

    comprobante_pago_filename = fields.Char(string='Nombre de archivo')

    estatus_layout = fields.Char(string='Estatus Layout',default='notready')

    relacion_layout = fields.Many2one('pagos_layout',string='Relación Layout')