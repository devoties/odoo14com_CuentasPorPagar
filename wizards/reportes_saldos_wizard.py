# -*- coding:utf-8 -*-

from odoo import fields, models, api


class SaldosWizard(models.TransientModel):


    _name = "reportes_saldos_wizard"

    #_inherit = 'account.move'

    def print(self):
        return self.env.ref('cuentas_por_pagar.report_estado_cuenta_card').report_action(self)
