# -*- coding:utf-8 -*-

from odoo import fields, models, api


class Cif(models.Model):
    _name = "cif"

    name = fields.Char(string='CIF',default='CIF')

    cif_filename = fields.Char(string='Nombre de archivo')

    cif_file = fields.Binary(string='Archivo Cif')

    fecha_emision = fields.Date(string='Fecha de emisión')

    cif_rel = fields.Many2one('res.partner',string='Cif Rel')
