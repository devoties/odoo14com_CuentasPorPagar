# -*- coding:utf-8 -*-
import base64
from odoo import fields, models, api, _
import logging
from datetime import datetime, date
from odoo.odoo.exceptions import UserError, ValidationError
logger = logging.getLogger(__name__)

class PagosLayout(models.Model):

    _name = "pagos_layout"

    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char(string='Referencia',copy=False,tracking=True,track_visibility='always',stored=True,required=True)

    fecha_reg = fields.Datetime(string='Fecha Layout',default=datetime.now(),tracking=True,track_visibility='always',stored=True,readonly=False,required=True)

    banco = fields.Many2one(comodel_name='res.bank',string='Banco Origen',tracking=True,track_visibility='always',stored=True)

    layout_type_bank = fields.Selection(string='Tipo de layout',
                                   selection=[
                                       ('santander_multiples_bancos','Santander Multiples Bancos'),
                                       ('santander_a_mismo_banco','Santander A Mismo Banco'),
                                       ('bbva_a_multiples_bancos','Bbva Multiples Bancos'),
                                       ('bbva_a_mismo_banco','Bbva Mismo Banco')
                                   ],default='santander_a_mismo_banco',copy=False,tracking=True,track_visibility='always',stored=True)

    relacion_pagos = fields.One2many('account.payment','relacion_layout',size=64,tracking=True,track_visibility='always',stored=True)

    layout_name = fields.Char(string='Contenedor de layout',size=64,default='layout.txt',tracking=True,track_visibility='always',stored=True)

    txt_layout_file = fields.Binary(string='Archivo de layout',tracking=True,track_visibility='always',stored=True,readonly=True)

    fecha_mod_layout = fields.Datetime(string='Fecha Cr/Mod Layout TXT',tracking=True,track_visibility='always',stored=True,readonly=True)

    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('validado', 'Validado'),
        ('cancelado','Cancelado')

    ], default='borrador', string='Estados', copy=False,tracking=True,track_visibility='always',stored=True)

    presupuestos_rel = fields.Many2one(string='Presupuesto',comodel_name='presupuesto_lotes')

    total_layout = fields.Float(string='Total Layout',compute='total_calculate')


    def total_calculate(self):
        total_lotes = 0.0
        for rec in self.relacion_pagos:
            print(rec.amount)
            total_lotes = total_lotes + rec.amount
        self.total_layout = total_lotes





    """
(0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
(1, ID, { values })    update the linked record with id = ID (write *values* on it)
(2, ID)                remove and delete the linked record with id = ID (calls unlink on ID, that will delete the object completely, and the link to it as well)
(3, ID)                cut the link to the linked record with id = ID (delete the relationship between the two objects but does not delete the target object itself)
(4, ID)                link to existing record with id = ID (adds a relationship)
(5)                    unlink all (like using (3,ID) for all linked records)
(6, 0, [IDs])          replace the list of linked IDs (like using (5) then (4,ID) for each ID in the list of IDs)
    """
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
                'active_ids': self.presupuestos_rel.lotes_provisionados.data_rel.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''

    def action_register_payment2(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.presupuestos_rel.facturas_adicionales.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''

    def pruebas(self):
        for r in self:
            pagos_ids = []
            r._cr.execute('''
                            SELECT id from account_payment 
                             ''')
            query_res = r._cr.dictfetchall()

            # idss = (1, 2, 3, 4, 5, 6, 7)

            for pys in query_res:
                pagos_ids.append(pys['id'])
            ids_payments_all = tuple(pagos_ids)

        for rec in self:
            lines = []
            for line in rec.presupuestos_rel.facturas_adicionales:
                lines.append(line.id)
            print(tuple(lines))
            tup_invoice_ids = tuple(lines)

            r._cr.execute('''SELECT
                payment.id as pay,
                payment.amount,
                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
				invoice.id,
				invoice.invoice_date,
                invoice.move_type
            FROM account_payment payment
            JOIN account_move move ON move.id = payment.move_id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
            JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
            JOIN account_move invoice ON invoice.id = counterpart_line.move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
                AND payment.id IN %(pays)s
                AND line.id != counterpart_line.id
                AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            	AND invoice.id IN %(account_move_ids)s
			GROUP BY payment.id, invoice.move_type, invoice.id, invoice.invoice_date''', {
                'pays': ids_payments_all,
                'account_move_ids': tup_invoice_ids,
            })
            query_res = r._cr.dictfetchall()
            pagos_ids_all = []
            pagos_ids_new = []
            payments_ids = ''
            lines = []

            for res in query_res:
                payments_ids = res['pay']
                pagos_ids_new.append(payments_ids)
                print('Nueva Imp')
                print(payments_ids)
                lines.append((4, int(payments_ids)))
        rec.relacion_pagos = lines

        for recx in self:
            linesx = []
            for linez in recx.presupuestos_rel.lotes_provisionados:
                print(linez.id_pago)
                linesx.append((4, int(linez.id_pago)))
            print("lines", linesx)

            #remueve los items del one2many
            #rec.relacion_pagos = ([2,int(line.id_pago)])
            #Obtiene los pagos relacionados con el presupuesto
        recx.relacion_pagos = linesx

    def delete_edit_validate(self):
        invoices_from_payment = self.relacion_pagos
        #print('primer dato',invoices_from_payment)
        for line_payment in invoices_from_payment:
            #print(line_payment.id)
            result = self.env['account.move'].search([('payment_id', '=', line_payment.id)]).ref
            #self._cr.execute('select ref FROM account_move where payment_id=%s'%(line_payment.id))
            #result = self._cr.fetchall()
            row_separator = ' '
            if result.count(row_separator) == 0:
                print('Fac Individuales: ')
                print(result)
                result = result
            if result.count(row_separator) > 0:
               print('Fac separadas: ')
               print(result.replace(' ', '\n'))
               result = result.replace(' ', '\n')


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
               dic = str(line.partner_id.name) + " " + str(line.partner_bank_id.acc_number) + " " + str(line.amount) + " " + str(line.recn) +\
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

        if self.layout_type_bank == 'santander_multiples_bancos':
           print('Layout TXT')
           file_layout_txt = open("odoo/addons_custom/cuentas_por_pagar/temp/layout_santander_multiples_bancos.txt", "w+")
           for line in self.relacion_pagos:
               dic = "65507540168" + "     " + str(line.partner_bank_id.acc_number) + "  " + str(line.bank_id_name_code) + "     " + str(line.partner_id.name) +\
                     "     " + str(line.amount) + "     " + str(line.recn) +\
                             "     "  + "N" + "     "+ "1" + "\n"
               print(dic)
               file_layout_txt.write(dic)

           file_layout_txt.close()

           file_layout_txt = open("odoo/addons_custom/cuentas_por_pagar/temp/layout_santander_multiples_bancos.txt", "rb+")
           out = file_layout_txt.read()

           file_layout_txt.close()

           self.txt_layout_file = base64.b64encode(out)

           self.layout_name = 'layout_santander_multiples_bancos.txt'

           self.write({'txt_layout_file': base64.b64encode(out), 'layout_name': 'layout_santander_multiples_bancos.txt'})

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
