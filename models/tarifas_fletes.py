# -*- coding:utf-8 -*-
from odoo import fields, models, api

class TarifasFletes(models.Model):
    _name = "tarifas_fletes"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    name = fields.Many2one(comodel_name='ciudad', string='Municipio')#funcina con y sin el comodel
    tipo_salida = fields.Selection(selection=[('normal', 'Normal'), ('rolado', 'Rolado')], string='Tipo de salida')
    impuestos = fields.Many2many(comodel_name='impuestos', string='Impuestos')
    importe = fields.Float(string='Importe')
    tarifa_importe_final_flete_municipio = fields.Float(string='Tarifa final', compute='_compute_tarifa_final')
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[('borrador', 'Borrador'), ('aprobado', 'Aprobado'),
                             ('bloqueo', 'bloqueo'), ]
                             , default='borrador', string='Estados', copy=False)

    testeo = fields.Many2many('fletes_modelo_tts', string='FLETES TESTEO')

    def _compute_tarifa_final(self):
        #iteras el modelo
        #
        for rec in self:
            res_impuesto = 0.0
            res_impuesto2 = 0.0
            for rec_line in rec.impuestos:
                print(rec_line.factor)
                print(rec_line.tipo_afectacion)
                if rec_line.tipo_afectacion == 'positive':
                    res_impuesto = (rec.importe) * (rec_line.factor / 100)
                    print('+')
                    print(res_impuesto)
                if rec_line.tipo_afectacion == 'negative':
                    res_impuesto2 = (rec.importe) * ((rec_line.factor / 100) * (-1))
                    print('-')
                    print(res_impuesto2)
                res_impuesto = res_impuesto + res_impuesto2

                print(res_impuesto,'fuera de los if')
            importe_original = rec.importe + res_impuesto


            rec.tarifa_importe_final_flete_municipio = importe_original

    def aprobar_tarifa_flete(self):
        self.state='aprobado'

    def modificar(self):
        self.state = 'borrador'



