# -*- coding:utf-8 -*-
import base64
from odoo import fields, models, api, _
import logging
from datetime import datetime, date
from odoo.odoo.exceptions import UserError, ValidationError
logger = logging.getLogger(__name__)

class AutorizacionesCancelaciones(models.Model):

    _name = "autorizaciones_cancelaciones"

    name = fields.Many2one('res.users',string='Solicitante',default=lambda self: self.env.user,readonly=True)

    invoice = fields.Many2one('account.move',string='Factura a cancelar',
                              domain = [('move_type', '=', 'in_invoice'),('payment_state','!=','not_paid')]
                              ,context="{'tree_view_ref':'account.view_in_invoice_tree'}")

    cancel_motive = fields.Selection(selection=[
        ('bad_invoice', 'Factura erronea'),
        ('invoice_dateless', 'Factura fuera de tiempo'),
        ('other','Otros')], default='bad_invoice', string='Motivo de cancelación', copy=False)

    motive = fields.Text(string='Motivo de cancelacion')