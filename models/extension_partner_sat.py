# -*- coding:utf-8 -*-

from odoo import fields, models, api


class ExtensionPartnersat(models.Model):

    _inherit = 'res.partner'
    # verifica que no se ingrese ningun contacto repedido
    # es funcional para el modulo de importacion de lotes SQL SERVER


    es_opinion_cumplimiento = fields.Boolean(string='¿OCOF?', default=True)

    opinion_cumplimiento = fields.One2many('opinion_cumplimiento_sat','opinion_cumplimiento_partner_rel',string='Opinión de cumplimiento')

    es_ine = fields.Boolean(string="¿INE?", default=True)

    ine = fields.One2many('ine_sat','ine_partner_rel',string='INE')

    es_cif = fields.Boolean(string='¿CSF?',default=True)

    cif_partner_rel = fields.One2many('cif','cif_rel',string='CSF')

    id_productor = fields.Integer(string='Id Productor TTS')

    id_jefe_cuadrilla = fields.Integer(string='Id Jefe Cuadrilla TTS')

    rfc = fields.Char(string='RFC')