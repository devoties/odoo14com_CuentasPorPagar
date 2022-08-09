# -*- coding:utf-8 -*-

from odoo import fields, models, api


class ReporteSaldos(models.Model):
    _name = "reporte_saldos"

    name = fields.Char(string='Referencia')

    fechai = fields.Date(string='De')

    fechaf = fields.Date(string='Hasta')

    lotes_no_facturados = fields.One2many('lotes','reporte_saldos_rel',string='Lotes No Facturados')

    lotes_facturados = fields.One2many('lotes_account_move_line','reporte_saldos_lotes_line_rel',string='Lotes Facturados')

    total_saldo = fields.Float(string='Total Saldo')

    def testing_calculate_not_paid(self):
        for l in self:
            lines_no_fac = []
            result_lotes_no_fac = l.env['lotes'].search([('lotes_detalle', '=', False)]).mapped("id")
            for line_no_fac in result_lotes_no_fac:
                lines_no_fac.append((4, int(line_no_fac)))
                print('Lotes No Facturados')
                print(line_no_fac)
        l.lotes_no_facturados = lines_no_fac
        for lx in self:
            lines_fac = []
            result_lotes_fac = lx.env['lotes_account_move_line'].search(['|',('estado_factura', '=', 'not_paid'),('estado_factura','=','partial')]).mapped("id")
            for line_fac in result_lotes_fac:
                lines_fac.append((4,int(line_fac)))
            lx.lotes_facturados = lines_fac

    def prueba_query(self):
        print('Prueba Query')
        function_get_report = self.env.ref['cuentas_por_pagar.lotes_view_report'].report_action(self,data=None)

        return function_get_report


class PruebaQuery(models.AbstractModel):
      _name = 'report.cuentas_por_pagar.lotes_report_new'
      _description = 'Reporte de saldos pendientes (Productores)'


      @api.model
      def _get_report_values(self,docs_ids,data=None):
          print('Query')
          vals = []
          query = """SELECT res_partner.name,sum(importe),count(res_partner.name)  FROM public.lotes
left join res_partner on public.lotes.id_partner  = res_partner.id
group by res_partner.name
order by res_partner.name ASC
                     """


          self._cr.execute(query)

          result = self._cr.fetchall()

          print(result)

          for l in result:
              vals.append({'name':l[0],
                           'imp':l[1],
                           'conteo':l[2],})

          return {

              'doc_ids': docs_ids,
              'vals': vals,
          }









"""    #INTEGRAR DATOS A UN ONE2MANY
        for recx in self:
            linesx = []
            for linez in recx.presupuestos_rel.lotes_provisionados:
                print(linez.id_pago)
                linesx.append((4, int(linez.id_pago)))
            print("lines", linesx)
"""
