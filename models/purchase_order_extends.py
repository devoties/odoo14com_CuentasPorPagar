# -- coding:utf-8 --

from odoo import fields, models, api

class OrdenesExtends(models.Model):

    _inherit = 'purchase.order'

    #account_move_rel = fields.Many2many('account.move','purchase_order_account_move_rel_4','account_id','purchase_id',string='Relacion Facturas')

    sale_order_count = fields.Integer(compute='_compute_sale_order_count',string='# of Sales Order', store=True)


    def update_all_products(self):
        x_prod = self.env['product.template'].search([])

        print(x_prod)
        x_prod.write({'default_code': '.'})
        self.env.cr.commit()
