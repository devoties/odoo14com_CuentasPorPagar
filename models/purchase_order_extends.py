# -- coding:utf-8 --

from odoo import fields, models, api

class OrdenesExtends(models.Model):

    _inherit = 'purchase.order'

    account_move_rel = fields.Many2many('account.move','account_move_purchase_order_rel_2',string='Relacion Facturas')