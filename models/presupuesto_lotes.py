from odoo import fields, models, api, _
from datetime import date,timedelta


class PresupuestoLotes(models.Model):
    _name = "presupuesto_lotes"
    _description = "Presupuesto de lotes"

    name = fields.Char(string='Referencia de presupuesto')

    fecha = fields.Datetime(string='Fecha de presupuesto')

    lotes_provisionados = fields.One2many('lotes_account_move_line','lotes_presupuestos_rel',string='Lotes Presupuestados')