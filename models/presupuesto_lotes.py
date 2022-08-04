from odoo import fields, models, api, _
from datetime import date,timedelta


class PresupuestoLotes(models.Model):
    _name = "presupuesto_lotes"
    _description = "Presupuesto de lotes"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='Referencia de presupuesto')

    fecha = fields.Datetime(string='Fecha de presupuesto')

    lotes_provisionados = fields.One2many('lotes_account_move_line','lotes_presupuestos_rel',string='Lotes Presupuestados')

    state = fields.Selection(string='Estatus',selection=[
        ('validate', 'Validado'),
        ('draft', 'Borrador'),

    ],copy=False, tracking=True, track_visibility='always', readonly=True,stored=True,default='draft')

    invoice_rel = fields.Many2one(string='Invoice Rel',related='lotes_provisionados.data_rel')

    payment_rel = fields.Char(string='Payment',related='invoice_rel.recn')

    payment_id_rel = fields.Char(string='Payment id',related='invoice_rel.id_pagos')

    budget_total = fields.Float(string='Total Presupuesto',compute='get_sum_budget')

    res = fields.Char(string='Estado de pago',compute='get_payment_state',stored=True)

    facturas_adicionales = fields.One2many('account.move','presupuesto_lote_fac_adic_rel')

    lotes_total = fields.Float(string='Total Lotes',compute='get_sum_lotes')

    aditional_invoices_total = fields.Float(string='Facturas adicionales Total',compute='get_sum_aditional_invoices')


    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.invoice_rel.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def get_sum_lotes(self):
            sum_budget = sum(self.env['lotes_account_move_line'].search([('lotes_presupuestos_rel','=',self.id)]).mapped('abono_importe_con_impuesto'))

            self.lotes_total = sum_budget

    def get_sum_aditional_invoices(self):
        total_facturas_adicionales = 0
        for l in self.facturas_adicionales:
            total_facturas_adicionales = total_facturas_adicionales + l.amount_residual_signed
        print(total_facturas_adicionales)
        self.aditional_invoices_total = (total_facturas_adicionales * -1)

    def get_sum_budget(self):
        sum_budget = sum(self.env['lotes_account_move_line'].search([('lotes_presupuestos_rel', '=', self.id)]).mapped(
            'abono_importe_con_impuesto'))

        total_facturas_adicionales = 0
        for l in self.facturas_adicionales:
            total_facturas_adicionales = total_facturas_adicionales + l.amount_residual_signed
        print(total_facturas_adicionales)
        self.budget_total = sum_budget + (total_facturas_adicionales * -1)


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

    def get_payment_state(self):
        for l in self:
            print('')
            counter_row = 0
            counter_paid_state = 0
            for linx in l.lotes_provisionados:
                counter_row = counter_row + 1
                if linx.estado_factura == 'paid':
                    counter_paid_state = counter_paid_state + 1
            if counter_row != counter_paid_state:
                l.res = 'Faltantes de pago'
            if counter_row == counter_paid_state and counter_row > 0 and counter_paid_state > 0:
                l.res = 'Pagado Completamente'
            if counter_row == 0 and counter_paid_state == 0:
                l.res = 'Documento en blanco'


