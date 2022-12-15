# -*- coding:utf-8 -*-
import base64
from odoo import fields, models, api, _
import logging
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError
logger = logging.getLogger(__name__)

class AutorizacionesCancelaciones(models.Model):

    _name = "autorizaciones_cancelaciones"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Many2one('res.users',string='Solicitante',default=lambda self: self.env.user,readonly=True,tracking=True,track_visibility='always',store=True)

    invoice = fields.Many2one('account.move',string='Factura a cancelar',
                              domain = [('move_type', '=', 'in_invoice'),('payment_state','!=','not_paid')]
                              ,context="{'tree_view_ref':'account.view_in_invoice_tree'}",tracking=True,track_visibility='always',store=True)

    cancel_motive = fields.Selection(selection=[
        ('bad_invoice', 'Factura erronea'),
        ('invoice_dateless', 'Factura fuera de tiempo'),
        ('other','Otros')], default='bad_invoice', string='Motivo de cancelación', copy=False,tracking=True,track_visibility='always',store=True)

    motive = fields.Text(string='Motivo de cancelacion',tracking=True,track_visibility='always',store=True)

    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('cancelado', 'Cancelado'),

    ], default='borrador', string='Estados', copy=False,tracking=True,track_visibility='always',store=True)


    def confirmar(self):
        print('confirmar')
        self.state = 'aprobado'
        #self.env['account.move'].write()
        inv_search = self.env['account.move'].search([('id', '=', self.invoice.id)], limit=1)

        self._cr.execute('update account_move set lock_validate=%s where id=%s', (True, inv_search.id))
    def cancelar(self):
        self.state = 'cancelado'
        inv_search = self.env['account.move'].search([('id', '=', self.invoice.id)], limit=1)

        self._cr.execute('update account_move set lock_validate=%s where id=%s', (None, inv_search.id))
