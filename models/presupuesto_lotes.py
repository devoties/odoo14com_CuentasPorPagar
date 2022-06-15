from odoo import fields, models, api, _
from datetime import date,timedelta


class PresupuestoLotes(models.Model):
    _name = "presupuesto_lotes"
    _description = "Presupuesto de lotes"

    name = fields.Char(string='Referencia de presupuesto')

    fecha = fields.Datetime(string='Fecha de presupuesto')

    lotes_provisionados = fields.One2many('lotes_account_move_line','lotes_presupuestos_rel',string='Lotes Presupuestados')

    state = fields.Selection(string='Estatus',selection=[
        ('validate', 'Validado'),
        ('draft', 'Borrador'),

    ],copy=False, tracking=True, track_visibility='always', readonly=True,stored=True)

    budget_total = fields.Float(string='Total Presupuesto',compute='get_sum_budget')

    def get_sum_budget(self):
            sum_budget = sum(self.env['lotes_account_move_line'].search([('lotes_presupuestos_rel','=',self.id)]).mapped('abono_importe_con_impuesto'))
            self.budget_total = sum_budget

    def budget_validate(self):
        lotes_linea_factura = self.env['lotes_account_move_line']
        self.state = 'validate'
        for line in self.lotes_provisionados:
            print(line.id)
            res = lotes_linea_factura.search([('id','=',line.id)])
            res.write({'lotes_status_lock':'lock'})
            self.env.cr.commit()

    def budget_draft(self):
        lotes_linea_factura = self.env['lotes_account_move_line']
        self.state = 'draft'
        for line in self.lotes_provisionados:
            print(line.id)
            res = lotes_linea_factura.search([('id','=',line.id)])
            res.write({'lotes_status_lock':'unlock'})
            self.env.cr.commit()