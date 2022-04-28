# -*- coding:utf-8 -*-
import base64
from odoo import fields, models, api
import logging
from datetime import datetime, date
from odoo.odoo.exceptions import UserError, ValidationError

logger = logging.getLogger(__name__)
class PagosLayout(models.Model):
    _name = "pagos_layout"

    name = fields.Char(string='Referencia')

    fecha_reg = fields.Datetime(string='Fecha Layout',default=datetime.now())

    banco = fields.Many2one(comodel_name='res.bank',string='Banco Origen')

    layout_type_bank = fields.Selection(string='Tipo de layout',
                                   selection=[
                                       ('santander_multiples_bancos','Santander Multiples Bancos'),
                                       ('santander_a_mismo_banco','Santander A Mismo Banco'),
                                       ('bbva_a_multiples_bancos','Bbva Multiples Bancos'),
                                       ('bbva_a_mismo_banco','Bbva Mismo Banco')
                                   ],default='santander_a_mismo_banco',copy=False)

    relacion_pagos = fields.One2many('account.payment','relacion_layout',size=64)

    layout_name = fields.Char(string='Contenedor de layout',size=64,default='layout.txt')

    txt_layout_file = fields.Binary(string='Archivo de layout',readonly=True)

    fecha_mod_layout = fields.Datetime(string='Fecha Cr/Mod Layout TXT',readonly=True)

    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('validado', 'Validado'),
        ('cancelado','Cancelado')

    ], default='borrador', string='Estados', copy=False)

    def delete_edit_validate(self):
        print('Validate')
        x=self.relacion_pagos.move_id
        for line in x:
            print(line)




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

    def default_bank(self):
        self.banco = self.env['res.bank'].search([('name', '=', 'SANTANDER')], limit=1).id

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
        if self.layout_type_bank == 'santander_a_mismo_banco':
           print('Layout TXT')
           file_layout_txt = open("odoo/addons_custom/cuentas_por_pagar/temp/layout_santander_mismo_banco.txt", "w+")
           for line in self.relacion_pagos:
               dic = str(line.partner_id.name) + " " + str(line.partner_bank_id.acc_number) + " " + str(line.amount) + " " + str(line.move_id.uuid) +\
                             " " + line.date.strftime('%d%m%Y') + f"\n"
               print(dic)
               file_layout_txt.write(dic)

           file_layout_txt.close()

           file_layout_txt = open("odoo/addons_custom/cuentas_por_pagar/temp/layout_santander_mismo_banco.txt", "rb+")
           out = file_layout_txt.read()

           file_layout_txt.close()

           self.txt_layout_file = base64.b64encode(out)

           self.layout_name = 'layout_santander_mismo_banco.txt'

           self.write({'txt_layout_file': base64.b64encode(out), 'layout_name': 'layout_santander_mismo_banco.txt'})

           self.fecha_mod_layout = datetime.now()



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
