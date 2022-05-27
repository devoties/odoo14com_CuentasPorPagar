# -- coding:utf-8 --

from odoo import fields, models, api

class OrdenesExtends(models.Model):

    _inherit = 'purchase.order'

    account_move_rel = fields.Many2many('account.move','account_move_purchase_order_rel_3',string='Relacion Facturas')

    sale_order_count = fields.Integer(compute='_compute_sale_order_count',string='# of Sales Order', store=True)
