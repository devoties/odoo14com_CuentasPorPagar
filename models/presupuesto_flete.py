# -*- coding:utf-8 -*-

from odoo import fields, models, api


class PresupuestoFlete(models.Model):
    _name = "presupuesto_flete"

    name = fields.Char(string='')
