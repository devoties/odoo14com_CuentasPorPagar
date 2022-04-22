# -*- coding:utf-8 -*-

from odoo import fields, models, api
import logging
from datetime import datetime
from odoo.odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)
class PagosLayout(models.Model):
    _name = "pagos_layout"

    name = fields.Char(string='Referencia')

    fecha_reg = fields.Datetime(string='Fecha Layout')

    banco = fields.Many2one(comodel_name='res.bank',string='Banco Origen')

    layout_type_bank = fields.Selection(string='Tipo de layout',
                                   selection=[
                                       ('santander_multiples_bancos','Santander Multiples Bancos'),
                                       ('santander_a_mismo_banco','Santander A Mismo Banco'),
                                       ('bbva_a_multiples_bancos','Bbva Multiples Bancos'),
                                       ('bbva_a_mismo_banco','Bbva Mismo Banco')
                                   ],default='santander_a_mismo_banco',copy=False)

    relacion_pagos = fields.One2many('account.payment','relacion_layout')

    txt_layout = fields.Binary(string='Txt Layout')

    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('validado', 'Validado'),
        ('cancelado','Cancelado')

    ], default='borrador', string='Estados', copy=False)



    def setStatusReady(self):
        for line in self:
            print('Prueba')

    def cancelar_layout(self):
        #self.state = 'borrador'
        self._cr.execute('update pagos_layout set state=%s where id=%s', ('borrador', self.id))
        for xline in self.relacion_pagos:
            print(xline.id)
            pago_id = self.env['account.payment'].browse([xline.id])
            print(self.env['account.payment'].browse([xline.id]))
            pago_id.write({'estatus_layout': 'notready'})
            self.env.cr.commit()



    @api.model
    def create(self, variables):
            modelo_layout_pago = super(PagosLayout, self).create(variables)
            logger.info('variables : {0}'.format(variables))
            return modelo_layout_pago

    def write(self, vals):
        if any(state == 'validado' for state in set(self.mapped('state'))):
            raise ValidationError("No se puede editar en estado 'validado'")
        else:
            return super().write(vals)


    def export_txt_layout(self):
        print('Layout TXT')
        for line in self.relacion_pagos:
            dic = {'partner_id':line.partner_id.name,
                   'partner_bank_id':line.partner_bank_id.acc_number,
                   'importe':line.amount,
                   'concepto':line.move_id,
                   'date':line.date.strftime('%Y-%m-%d')}

            print(dic)




    def printPdf(self):
        print('PRINT PDF')

    def confirmLayout(self):
        print('Confirm Layout')
        for xline in self.relacion_pagos:
            print(xline.id)
            pago_id = self.env['account.payment'].browse([xline.id])
            print(self.env['account.payment'].browse([xline.id]))
            pago_id.write({'estatus_layout': 'locked'})
            self.env.cr.commit()
        self.state = 'validado'
