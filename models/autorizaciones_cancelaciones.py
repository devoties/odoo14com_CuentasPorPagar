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

    invoice = fields.Many2one('account.move',string='Factura a cancelar')

