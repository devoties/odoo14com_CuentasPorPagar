# -*- coding:utf-8 -*-
from odoo import fields, models, api

class FletW(models.TransientModel):
    _name = "fletes_wizard"
    fecha_inicial = fields.Date(string='Fecha inicial',store=True)
    fecha_final = fields.Date(string='Fecha final',store=True)

    def method_a(self):
        self.env['fletes_modelo_tts'].download_data()

    @api.model_create_multi
    def create(self, vals):
        rec = super(FletW, self).create(vals)
        return rec 
