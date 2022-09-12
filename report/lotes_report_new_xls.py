# -*- coding:utf-8 -*-

from odoo import fields, models, api
#Listo
class PruebaQueryExcel(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_new_xls'
    _description = 'Reporte de saldos pendientes (Productores)'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data,row_count):

        #print('Query')
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end
        query_filter_provider = ''

        if i.provider_type == 'todo':
            query_filter_provider = ''
        if i.provider_type == 'productor':
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '

        query = f""" SELECT res_partner.name,sum(importe) as importe,count(res_partner.name),
                     case when lotes_account_move_line.name is not null then 'Facturado' else 'No Facturado' end as estatus
                     FROM public.lotes
                     left join res_partner on public.lotes.id_partner  = res_partner.id
                     left join lotes_account_move_line on public.lotes.id = lotes_account_move_line.name
                     where case when lotes_account_move_line.name is not null then 'Facturado' else 'No Facturado' end = 'No Facturado'
                     and public.lotes.fecha between '{i.date_start}' and '{i.date_end}'
                     {query_filter_provider}
                     group by res_partner.name,case when lotes_account_move_line.name is not null then 'Facturado' else 'No Facturado' end
                     order by res_partner.name ASC;
                     """
        self._cr.execute(query)
        #print('Saldos Fruta X Pagar55555')
        result = self._cr.fetchall()

        #print(result)
        row_count = 0
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter',})
        sheet = workbook.add_worksheet('Reporte 1')
        for lines in result:
            row_count = row_count + 1
            print('resssss')
            print(lines[0])
            print('Lineaaaa de testingggg')
            print(lines)
            sheet.set_column(3, 3, 50)
            sheet.set_column(2, 2, 30)
            sheet.write(0, 0, 'Nombre', format1)
            sheet.write(row_count, 0, lines[0],format2)
            sheet.write(0, 1, 'Importe', format1)
            sheet.write(row_count, 1, lines[1], format2)
            sheet.write(0, 2, 'Cant Lotes', format1)
            sheet.write(row_count, 2, lines[2], format2)


# Completo
class FacturadonoPagadoExcel(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_facturado_no_pagado_xls'
    _description = 'Reporte de facturado no pagado (Productores) XLSX'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def generate_xlsx_report(self, workbook, data,row_count):
        print('Query')
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end
        query_filter_provider = ''
        query_extra_invoices = ''
        var_date_type_ctrl = ''
        if i.provider_type == 'todo':
            query_filter_provider = ''
            query_extra_invoices = ''

        if i.provider_type == 'productor':
            query_extra_invoices = f''
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '
        if i.provider_type == 'emisor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.account_move.partner_id =  {i.productor_id.id} '
        query_union_value_original = f"""

                   union all
                   select
                   account_move.uuid as uuid,
                   res_partner.name as name,
                   sum(account_move.amount_residual)::numeric as saldo_pendiente,
                   count(account_move.uuid) as conteo
                   FROM account_move 
                   left join res_partner on account_move.partner_id = res_partner.id
                   WHERE NOT exists
                   (SELECT data_rel
                   FROM lotes_account_move_line p
                   WHERE p.data_rel = account_move.id)
                   and account_move.move_type = 'in_invoice'
                   and account_move.date between '{i.date_start}' and '{i.date_end}'
                   and account_move.state = 'posted'
                   and account_move.payment_state != 'paid'
                   {query_extra_invoices}
                   group by res_partner.name,account_move.uuid
                   order by name """
        query_union_extra_invoice = ''

        if i.date_type == 'fecha_factura':
            var_date_type_ctrl = 'account_move.date'
            query_union_extra_invoice = query_union_value_original
        if i.date_type == 'fecha_lote':
            var_date_type_ctrl = 'lotes.fecha'
            query_union_extra_invoice = ''

        vals = []
        query = f"""SELECT public.lotes_account_move_line.uuid,
                   public.res_partner.name,
                   sum(case when account_move.total_impuestos_retenidos > 0 then (lotes_account_move_line.abono_kilogramos * lotes.precio_u) - 
                   ((lotes_account_move_line.abono_kilogramos * lotes.precio_u) * (0.0125)) 
                   else (lotes_account_move_line.abono_kilogramos * lotes.precio_u) end)::numeric as saldo_pendiente,
                   COUNT(public.lotes_account_move_line.uuid) as conteo
                   FROM public.lotes_account_move_line
                   left join public.lotes on public.lotes_account_move_line.name = public.lotes.id
                   left join public.res_partner on public.lotes.id_partner = public.res_partner.id
                   left join public.account_move on public.lotes_account_move_line.data_rel = public.account_move.id
                   where public.account_move.amount_residual>0
                   and public.{var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
                   {query_filter_provider}
                   group by public.lotes_account_move_line.uuid,public.account_move.partner_id,public.res_partner.name
                   {query_union_extra_invoice}
                     """

        self._cr.execute(query)

        result = self._cr.fetchall()

        print('Facturado No Pagado')

        print(result)

        row_count = 0
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter',})
        sheet = workbook.add_worksheet('Reporte 1')
        for lines in result:
            row_count = row_count + 1
            print('resssss')
            print(lines[0])
            print('Lineaaaa de testingggg')
            print(lines)
            sheet.set_column(3, 3, 50)
            sheet.set_column(2, 2, 30)
            sheet.write(0, 0, 'Uuid', format1)
            sheet.write(row_count, 0, lines[0],format2)
            sheet.write(0, 1, 'Nombre', format1)
            sheet.write(row_count, 1, lines[1], format2)
            sheet.write(0, 2, 'Importe', format1)
            sheet.write(row_count, 2, lines[2], format2)
