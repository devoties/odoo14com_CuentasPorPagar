# -*- coding:utf-8 -*-

from odoo import fields, models, api


class CortesWizard(models.TransientModel):

    _name = "cortes_wizard"

    #_inherit = 'cortes'

    fecha_inicial = fields.Date(string='Fecha inicial')

    fecha_final = fields.Date(string='Fecha final')


    def method_a(self):
        self.env['cortes'].download_data()

    def buscarDatosH(self):
        self.env['cortes'].buscarDatos()

    @api.model_create_multi
    def create(self,vals):

        rec = super(CortesWizard,self).create(vals)
        return rec
