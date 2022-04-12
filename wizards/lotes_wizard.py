# -*- coding:utf-8 -*-

from odoo import fields, models, api


class LotesWizard(models.TransientModel):

    _name = "lotes_wizard"

    #_inherit = 'lotes'

    fecha_inicial = fields.Date(string='Fecha inicial')

    fecha_final = fields.Date(string='Fecha final')


    def method_a(self):
        self.env['lotes'].download_data()

    @api.model_create_multi
    def create(self,vals):

        rec = super(LotesWizard,self).create(vals)
        return rec
