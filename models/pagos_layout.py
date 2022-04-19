# -*- coding:utf-8 -*-

from odoo import fields, models, api
import logging
logger = logging.getLogger(__name__)
class PagosLayout(models.Model):
    _name = "pagos_layout"

    name = fields.Char(string='Referencia')

    fecha_reg = fields.Datetime(string='Fecha Layout')

    banco = fields.Many2one(comodel_name='res.bank')

    relacion_pagos = fields.One2many('account.payment','relacion_layout')

    def setStatusReady(self):
        for line in self:
            print('Prueba')

    @api.model
    def create(self, variables):
            modelo_layout_pago = super(PagosLayout, self).create(variables)
            logger.info('variables : {0}'.format(variables))
            prueba = variables['relacion_pagos']
            for line in prueba:
                print(line)
            return modelo_layout_pago


    def export_txt_layout(self):
        print('Layout TXT')

    def printPdf(self):
        print('PRINT PDF')

    def confirmLayout(self):
        print('Confirm Layout')