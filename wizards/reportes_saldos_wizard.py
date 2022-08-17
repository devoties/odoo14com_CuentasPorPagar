# -*- coding:utf-8 -*-

from odoo import fields, models, api


class SaldosWizard(models.TransientModel):


    _name = "reportes_saldos_wizard"

    #_inherit = 'account.move'

    def print_no_facturado(self):
        return self.env.ref('cuentas_por_pagar.report_estado_cuenta_card').report_action(self)
    def print_facturado_no_pagado(self):
        return self.env.ref('cuentas_por_pagar.report_lotes_facturado_no_pagado').report_action(self)
    def print3(self):
        return self.env.ref('cuentas_por_pagar.report_lotes_fac_no_pag_no_fac_no_pag').report_action(self)
    def print_fact_no_pagado_datelle(self):
        return self.env.ref('cuentas_por_pagar.report_lotes_fac_no_pag_detail').report_action(self)
    def print_no_fac_datelle(self):
        return self.env.ref('cuentas_por_pagar.report_lotes_no_fac_detall').report_action(self)