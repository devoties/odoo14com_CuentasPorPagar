# -*- coding:utf-8 -*-

from odoo import fields, models, api
from datetime import datetime

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




#completo
class PruebaQuery(models.AbstractModel):
      _name = 'report.cuentas_por_pagar.lotes_report_new'
      _description = 'Reporte de saldos pendientes (Productores)'


      @api.model
      def _get_report_values(self,docs_ids,data=None):
          print('Query')
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

          vals = []
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
          print('Saldos Fruta X Pagar')
          result = self._cr.fetchall()

          print(result)

          for l in result:
              vals.append({'name':l[0],
                           'imp':l[1],
                           'conteo':l[2],})

          return {

              'doc_ids': docs_ids,
              'vals': vals,
              'date_start': i.date_start,
              'date_end': i.date_end,
          }

#Completo
class FacturadonoPagado(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_new_facturado_no_pagado'
    _description = 'Reporte de facturado no pagado (Productores)'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
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

        for l in result:
            vals.append({'uuid': l[0],
                         'proveedor': l[1],
                         'saldo_pendiente': l[2], })

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }
#Completo
class FacturadonopagadoDetallado(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_fac_no_pag_detall'
    _description = 'Reporte de facturado no pagado detallado (Productores)'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end
            i.date_type
        #variable de control para intercambiar tabla en el query dependiendo que
        #opcion del selection se utilice (dato almacenado en la bd)
        var_date_type_ctrl = ''
        query_filter_provider = ''
        query_extra_invoices = ''
        # Filtro proveedor
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
                   null as lote,
                   res_partner.name as proveedor,
                   null as huerta,
                   sum(account_move.amount_residual)::numeric as saldo_new,
                   null as pago_por_lote,
                   null as kg_abono,
                   null as precio_u,
                   null as tipo_ret,
                   null as conteo
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
                   group by res_partner.name,account_move.uuid """
        query_union_extra_invoice = ''
        #Filtro fechas
        if i.date_type == 'fecha_factura':
            var_date_type_ctrl = 'account_move.date'
            query_union_extra_invoice = query_union_value_original
        if i.date_type == 'fecha_lote':
            var_date_type_ctrl = 'lotes.fecha'
            query_union_extra_invoice = ''

        if i.date_type == 'fecha_factura' and i.provider_type == 'productor':
            query_union_extra_invoice = ''

        print('fecha calis')
        print(i.date_type)
        vals = []
        query = f"""SELECT public.lotes_account_move_line.uuid as uuid,
                   public.lotes.name as lote,
                   public.res_partner.name as proveedor,
                   public.huertas.name as huerta,
                   case when public.account_move.amount_residual < public.account_move.amount_total then
                   (public.lotes_account_move_line.abono_kilogramos * public.lotes.precio_u)-((public.lotes_account_move_line.abono_kilogramos * public.lotes.precio_u)*(0.0125))
                   else  public.lotes_account_move_line.abono_kilogramos * public.lotes.precio_u
                   end::numeric as saldo_new,
                   public.lotes_account_move_line.abono_kilogramos * public.lotes.precio_u as pago_por_lote,
                   public.lotes_account_move_line.abono_kilogramos as kg_abono,
                   round(cast((public.lotes.precio_u) as decimal),2) AS precio_u,
                   case when public.account_move.amount_residual < public.account_move.amount_total then 'RET 1.25%' else 'Tasa 0' end as tipo_ret,
                   public.lotes.fecha as fecha
                   FROM public.lotes_account_move_line
                   left join public.lotes on public.lotes_account_move_line.name = public.lotes.id
                   left join public.res_partner on public.lotes.id_partner = public.res_partner.id
                   left join public.account_move on public.lotes_account_move_line.data_rel = public.account_move.id
                   left join public.huertas on public.lotes.sader = public.huertas.id
                   where public.account_move.amount_residual>0
                   and public.{var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
                   {query_filter_provider}
                   {query_union_extra_invoice}
                   order by proveedor,uuid,huerta asc
                     """

        self._cr.execute(query)

        result = self._cr.fetchall()

        print(result)

        print('Facturas por pagar Detalle')

        for l in result:
            vals.append({'uuid': l[0],
                         'lote': l[1],
                         'proveedor': l[2],
                         'huerta': l[3],
                         'saldo_new': l[4],
                         'kg_abono': l[6],
                         'precio_u':l[7],
                         'tipo_ret':[8]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }

#No facturado
#Completo
class NofacturadoDetalle(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_no_fac_datall'
    _description = 'Reporte de facturado no pagado detallado (Productores)'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end

        query_filter_provider = ''
        # Filtro proveedor
        if i.provider_type == 'todo':
            query_filter_provider = ''

        if i.provider_type == 'productor':
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '

        print('Query')
        vals = []
        query = f"""select public.lotes.name as lote,
                   public.res_partner.name as proveedor,
                   public.huertas.sader as sader,
                   public.lotes.fecha as fecha,
                   public.lotes.importe as importe,
                   public.lotes.precio_u as precio_u,
                   public.lotes.cantidad as cantidad,
                   public.lotes.tipo_corte as tipo_corte,
                   public.huertas.name as huerta
                   from public.lotes
                   left join public.lotes_account_move_line on public.lotes.id = public.lotes_account_move_line.name
                   left join public.huertas on public.lotes.sader = public.huertas.id
                   left join public.res_partner on public.lotes.id_partner = public.res_partner.id
                   where public.lotes_account_move_line.uuid is null
                   and public.lotes.fecha between '{i.date_start}' and '{i.date_end}'
                   {query_filter_provider}
                   order by public.res_partner.name,public.huertas.sader,public.lotes.fecha asc
                     """

        self._cr.execute(query)

        result = self._cr.fetchall()

        print(result)

        print('Pendiente de factura detalle')

        for l in result:
            vals.append({'lote': l[0],
                         'proveedor': l[1],
                         'sader': l[2],
                         'fecha': l[3],
                         'importe': l[4],
                         'precio_u': l[5],
                         'cantidad':l[6],
                         'tipo_corte':l[7],
                         'huerta':l[8]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }




#Fin no facturaod


#Pagado
#Completo
class Pagado(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_pagado'
    _description = 'Reporte Pagado (Productores)'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        vals = []
        q_payments_tuple = """SELECT id FROM public.account_payment order by id asc"""

        self._cr.execute(q_payments_tuple)

        res_payments_tuple = self._cr.fetchall()

        #print(res_payments_tuple)
        list_tuple = []
        for line in res_payments_tuple:
            list_tuple.append(line[0])
        list_tuple = tuple(list_tuple)

        q_invoice_tuple = """SELECT id FROM public.account_move WHERE move_type = 'in_invoice' order by id asc"""

        self._cr.execute(q_invoice_tuple)

        res_invoice_tuple = self._cr.fetchall()

        #Add view partial payments

        q_partial_payments = """ CREATE OR REPLACE VIEW partial_payments AS SELECT ap.debit_move_id,ap.credit_move_id,ap.amount,account_move_line.move_id FROM public.account_partial_reconcile as ap
                                left join account_move_line on ap.credit_move_id  = account_move_line.id
                                ORDER BY debit_move_id desc;
                             """
        self._cr.execute(q_partial_payments)

        #print(res_payments_tuple)
        list_tuple_invoice = []
        for line_invoice in res_invoice_tuple:
            list_tuple_invoice.append(line_invoice[0])
        list_tuple_invoice = tuple(list_tuple_invoice)

        q_view_payments_invoices = f"""CREATE OR REPLACE VIEW pagado AS SELECT 
                payment.id as payment_id,
                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
				invoice.id as inv_id,
				move.date as fechax,
                invoice.move_type as move_type,
                sum(payment.amount) as amount
            FROM account_payment payment
            JOIN account_move move ON move.id = payment.move_id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
            JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
            JOIN account_move invoice ON invoice.id = counterpart_line.move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
                AND payment.id IN {list_tuple}
                AND line.id != counterpart_line.id
                AND invoice.move_type in ('in_invoice')
            	AND invoice.id IN {list_tuple_invoice}
			GROUP BY payment.id, invoice.move_type, invoice.id, fechax;
            CREATE OR REPLACE VIEW pagado_por_factura AS 
            select inv_id,sum(amount) as amount FROM public.pagado
            group by inv_id;
            SELECT * FROM pagado_por_factura;"""

        self._cr.execute(q_view_payments_invoices)

        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end

        var_date_type_ctrl = ''
        query_filter_provider = ''
        query_extra_invoices = ''
        if i.date_type == 'fecha_pago':
            var_date_type_ctrl = 'pagado.fechax'
        if i.provider_type == 'todo':
            query_filter_provider = ''
            query_extra_invoices = ''
        if i.provider_type == 'productor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '
        if i.provider_type == 'emisor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.account_move.partner_id =  {i.productor_id.id} '

#Aun no lo utilizo preguntar como sacariamos los anticipos y facturas adicionales
        q_pagado = f"""select public.res_partner.name,
                   sum(case when account_move.total_impuestos_retenidos > 0 then (lotes_account_move_line.abono_kilogramos * lotes.precio_u) - 
                   ((lotes_account_move_line.abono_kilogramos * lotes.precio_u) * (0.0125)) 
                   else (lotes_account_move_line.abono_kilogramos * lotes.precio_u) end) as importe_pagado
                   FROM public.lotes_account_move_line
                   left join public.lotes on public.lotes_account_move_line.name = public.lotes.id
                   left join public.account_move on public.lotes_account_move_line.data_rel = public.account_move.id
                   left join public.res_partner on public.account_move.partner_id = public.res_partner.id
                   left join public.pagado_por_factura on public.lotes_account_move_line.data_rel = public.pagado_por_factura.inv_id
                   left join public.pagado on public.lotes_account_move_line.data_rel = public.pagado.inv_id
                   where public.account_move.amount_residual = 0
                   {query_filter_provider}
                   and public.{var_date_type_ctrl}  between '{i.date_start}' and '{i.date_end}'
                   group by public.res_partner.name
                   union all            
                   SELECT res_partner.name,
                   sum(pagado_por_factura.amount) as amount
                   FROM account_move 
                   left join pagado on account_move.id = pagado.inv_id 
                   left join res_partner on account_move.partner_id = res_partner.id
                   left join pagado_por_factura on account_move.id = pagado_por_factura.inv_id
                   WHERE NOT exists
                   (SELECT data_rel
                   FROM lotes_account_move_line p
                   WHERE p.data_rel = account_move.id)
                   and account_move.move_type = 'in_invoice'
                   and account_move.payment_state = 'paid'
                   and public.{var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
                   {query_extra_invoices}
                   group by res_partner.name
        """


        self._cr.execute(q_pagado)

        res_q_pagado = self._cr.fetchall()

        print(res_q_pagado)

        for lnxx in res_q_pagado:
            vals.append({'name': lnxx[0],
                         'importe_pagado':lnxx[1]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }


# Pagado por productor
#Completo
class PagadoporProductor(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_pagado_prod'
    _description = 'Reporte Pagado X (Productor)'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        vals = []
        q_payments_tuple = """SELECT id FROM public.account_payment order by id asc"""

        self._cr.execute(q_payments_tuple)

        res_payments_tuple = self._cr.fetchall()

        # print(res_payments_tuple)
        list_tuple = []
        for line in res_payments_tuple:
            list_tuple.append(line[0])
        list_tuple = tuple(list_tuple)

        #Add view partial payments

        q_partial_payments = """ CREATE OR REPLACE VIEW partial_payments AS SELECT ap.debit_move_id,ap.credit_move_id,ap.amount,account_move_line.move_id FROM public.account_partial_reconcile as ap
                                left join account_move_line on ap.credit_move_id  = account_move_line.id
                                ORDER BY debit_move_id desc;
                             """
        self._cr.execute(q_partial_payments)

        q_invoice_tuple = """SELECT id FROM public.account_move WHERE move_type = 'in_invoice' order by id asc"""

        self._cr.execute(q_invoice_tuple)

        res_invoice_tuple = self._cr.fetchall()

        # print(res_payments_tuple)
        list_tuple_invoice = []
        for line_invoice in res_invoice_tuple:
            list_tuple_invoice.append(line_invoice[0])
        list_tuple_invoice = tuple(list_tuple_invoice)

        q_view_payments_invoices = f"""CREATE OR REPLACE VIEW pagado AS SELECT 
                payment.id as payment_id,
                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
				invoice.id as inv_id,
				move.date as fechax,
                invoice.move_type as move_type,
                sum(payment.amount) as amount

            FROM account_payment payment
            JOIN account_move move ON move.id = payment.move_id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
            JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
            JOIN account_move invoice ON invoice.id = counterpart_line.move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
                AND payment.id IN {list_tuple}
                AND line.id != counterpart_line.id
                AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            	AND invoice.id IN {list_tuple_invoice}
			GROUP BY payment.id, invoice.move_type, invoice.id, fechax;
            CREATE OR REPLACE VIEW pagado_por_factura AS 
            select inv_id,sum(amount) as amount FROM public.pagado
            group by inv_id;
            SELECT * FROM pagado_por_factura;"""

        self._cr.execute(q_view_payments_invoices)

        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end

        var_date_type_ctrl = ''
        query_filter_provider = ''
        query_extra_invoices = ''
        if i.date_type == 'fecha_pago':
            var_date_type_ctrl = 'pagado.fechax'
        if i.provider_type == 'todo':
            query_filter_provider = ''
            query_extra_invoices = ''
        if i.provider_type == 'productor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '
        if i.provider_type == 'emisor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.account_move.partner_id =  {i.productor_id.id} '

        # Aun no lo utilizo preguntar como sacariamos los anticipos y facturas adicionales
        q_pagado = f"""select public.res_partner.name,
                   sum(case when account_move.total_impuestos_retenidos > 0 then (lotes_account_move_line.abono_kilogramos * lotes.precio_u) - 
                   ((lotes_account_move_line.abono_kilogramos * lotes.precio_u) * (0.0125)) 
                   else (lotes_account_move_line.abono_kilogramos * lotes.precio_u) end)::numeric as importe_pagado
                   FROM public.lotes_account_move_line
                   left join public.lotes on public.lotes_account_move_line.name = public.lotes.id
                   left join public.res_partner on public.lotes.id_partner = public.res_partner.id
                   left join public.account_move on public.lotes_account_move_line.data_rel = public.account_move.id
                   left join public.pagado_por_factura on public.lotes_account_move_line.data_rel = public.pagado_por_factura.inv_id
                   left join public.pagado on public.lotes_account_move_line.data_rel = public.pagado.inv_id
                   where public.account_move.amount_residual = 0
                   {query_filter_provider}
                   and public.{var_date_type_ctrl}  between '{i.date_start}' and '{i.date_end}'
                   group by public.res_partner.name
                   union all            
                   SELECT res_partner.name,
                   sum(pagado_por_factura.amount)::numeric as amount
                   FROM account_move 
                   left join pagado on account_move.id = pagado.inv_id 
                   left join res_partner on account_move.partner_id = res_partner.id
                   left join pagado_por_factura on account_move.id = pagado_por_factura.inv_id
                   WHERE NOT exists
                   (SELECT data_rel
                   FROM lotes_account_move_line p
                   WHERE p.data_rel = account_move.id)
                   and account_move.move_type = 'in_invoice'
                   and account_move.payment_state = 'paid'
                   and public.{var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
                   {query_extra_invoices}
                   group by res_partner.name
        """

        self._cr.execute(q_pagado)

        res_q_pagado = self._cr.fetchall()

        print(res_q_pagado)

        for lnxx in res_q_pagado:
            vals.append({'name': lnxx[0],
                         'importe_pagado': lnxx[1]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }
#Completo
class PagadoporProductorDetalle(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_pagado_prod_det'
    _description = 'Reporte Pagado X (Productor) Detalle'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        vals = []

        #Add view partial payments

        q_partial_payments = """ CREATE OR REPLACE VIEW partial_payments AS SELECT ap.debit_move_id,ap.credit_move_id,ap.amount,account_move_line.move_id FROM public.account_partial_reconcile as ap
                                left join account_move_line on ap.credit_move_id  = account_move_line.id
                                ORDER BY debit_move_id desc;
                             """
        self._cr.execute(q_partial_payments)

        q_payments_tuple = """SELECT id FROM public.account_payment order by id asc"""

        self._cr.execute(q_payments_tuple)

        res_payments_tuple = self._cr.fetchall()

        # print(res_payments_tuple)
        list_tuple = []
        for line in res_payments_tuple:
            list_tuple.append(line[0])
        list_tuple = tuple(list_tuple)

        q_invoice_tuple = """SELECT id FROM public.account_move WHERE move_type = 'in_invoice' order by id asc"""

        self._cr.execute(q_invoice_tuple)

        res_invoice_tuple = self._cr.fetchall()

        # print(res_payments_tuple)
        list_tuple_invoice = []
        for line_invoice in res_invoice_tuple:
            list_tuple_invoice.append(line_invoice[0])
        list_tuple_invoice = tuple(list_tuple_invoice)

        q_view_payments_invoices = f"""CREATE OR REPLACE VIEW pagado AS SELECT 
                payment.id as payment_id,
                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
				invoice.id as inv_id,
				move.date as fechax,
                invoice.move_type as move_type,
                sum(payment.amount) as amount

            FROM account_payment payment
            JOIN account_move move ON move.id = payment.move_id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
            JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
            JOIN account_move invoice ON invoice.id = counterpart_line.move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
                AND payment.id IN {list_tuple}
                AND line.id != counterpart_line.id
                AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            	AND invoice.id IN {list_tuple_invoice}
			GROUP BY payment.id, invoice.move_type, invoice.id, fechax;
            CREATE OR REPLACE VIEW pagado_por_factura AS 
            select inv_id,sum(amount) as amount FROM public.pagado
            group by inv_id;
            SELECT * FROM pagado_por_factura;"""

        self._cr.execute(q_view_payments_invoices)

        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end

        var_date_type_ctrl = ''
        query_filter_provider = ''
        query_extra_invoices = ''
        if i.date_type == 'fecha_pago':
            var_date_type_ctrl = 'pagado.fechax'
        if i.provider_type == 'todo':
            query_filter_provider = ''
            query_extra_invoices = ''
        if i.provider_type == 'productor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '
        if i.provider_type == 'emisor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.account_move.partner_id =  {i.productor_id.id} '

        # Aun no lo utilizo preguntar como sacariamos los anticipos y facturas adicionales
        q_pagado = f"""select public.res_partner.name,
                   case when account_move.total_impuestos_retenidos > 0 then (lotes_account_move_line.abono_kilogramos * lotes.precio_u) - 
                   ((lotes_account_move_line.abono_kilogramos * lotes.precio_u) * (0.0125)) 
                   else (lotes_account_move_line.abono_kilogramos * lotes.precio_u) end::numeric as importe_pagado,
                   lotes.name as lote,
                   lotes_account_move_line.uuid as uuid,
                   huertas.name as sader
                   FROM public.lotes_account_move_line
                   left join public.lotes on public.lotes_account_move_line.name = public.lotes.id
                   left join public.res_partner on public.lotes.id_partner = public.res_partner.id
                   left join public.account_move on public.lotes_account_move_line.data_rel = public.account_move.id
                   left join public.pagado_por_factura on public.lotes_account_move_line.data_rel = public.pagado_por_factura.inv_id
                   left join public.pagado on public.lotes_account_move_line.data_rel = public.pagado.inv_id
                   left join public.huertas on public.lotes.sader = public.huertas.id 
                   where public.account_move.amount_residual = 0
                   {query_filter_provider}
                   and public.{var_date_type_ctrl}  between '{i.date_start}' and '{i.date_end}'
                   union all            
                   SELECT res_partner.name,
                   sum(pagado_por_factura.amount)::numeric as amount,
                   null as lote,
                   account_move.uuid,
                   null as sader
                   FROM account_move 
                   left join pagado on account_move.id = pagado.inv_id 
                   left join res_partner on account_move.partner_id = res_partner.id
                   left join pagado_por_factura on account_move.id = pagado_por_factura.inv_id                   
                   WHERE NOT exists
                   (SELECT data_rel
                   FROM lotes_account_move_line p
                   WHERE p.data_rel = account_move.id)
                   and account_move.move_type = 'in_invoice'
                   and account_move.payment_state = 'paid'
                   and {var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
                   {query_extra_invoices}
                   group by res_partner.name,account_move.uuid
                   order by name
        """

        self._cr.execute(q_pagado)

        res_q_pagado = self._cr.fetchall()

        print(res_q_pagado)

        for lnxx in res_q_pagado:
            vals.append({'name': lnxx[0],
                         'importe_pagado': lnxx[1],
                         'lote':lnxx[2],
                         'uuid':lnxx[3],
                         'sader':lnxx[4]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }
#Completo
class PagadoporEmisorDetalle(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_report_pagado_emi_det'
    _description = 'Reporte Pagado X (Emisor) Detalle'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        vals = []

        #Add view partial payments

        q_partial_payments = """ CREATE OR REPLACE VIEW partial_payments AS SELECT ap.debit_move_id,ap.credit_move_id,ap.amount,account_move_line.move_id FROM public.account_partial_reconcile as ap
                                left join account_move_line on ap.credit_move_id  = account_move_line.id
                                ORDER BY debit_move_id desc;
                             """
        self._cr.execute(q_partial_payments)

        q_payments_tuple = """SELECT id FROM public.account_payment order by id asc"""

        self._cr.execute(q_payments_tuple)

        res_payments_tuple = self._cr.fetchall()

        # print(res_payments_tuple)
        list_tuple = []
        for line in res_payments_tuple:
            list_tuple.append(line[0])
        list_tuple = tuple(list_tuple)

        q_invoice_tuple = """SELECT id FROM public.account_move WHERE move_type = 'in_invoice' order by id asc"""

        self._cr.execute(q_invoice_tuple)

        res_invoice_tuple = self._cr.fetchall()

        # print(res_payments_tuple)
        list_tuple_invoice = []
        for line_invoice in res_invoice_tuple:
            list_tuple_invoice.append(line_invoice[0])
        list_tuple_invoice = tuple(list_tuple_invoice)

        q_view_payments_invoices = f"""CREATE OR REPLACE VIEW pagado AS SELECT 
                payment.id as payment_id,
                ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
				invoice.id as inv_id,
				move.date as fechax,
                invoice.move_type as move_type,
                sum(payment.amount) as amount

            FROM account_payment payment
            JOIN account_move move ON move.id = payment.move_id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_partial_reconcile part ON
                part.debit_move_id = line.id
                OR
                part.credit_move_id = line.id
            JOIN account_move_line counterpart_line ON
                part.debit_move_id = counterpart_line.id
                OR
                part.credit_move_id = counterpart_line.id
            JOIN account_move invoice ON invoice.id = counterpart_line.move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
                AND payment.id IN {list_tuple}
                AND line.id != counterpart_line.id
                AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
            	AND invoice.id IN {list_tuple_invoice}
			GROUP BY payment.id, invoice.move_type, invoice.id, fechax;
            CREATE OR REPLACE VIEW pagado_por_factura AS 
            select inv_id,sum(amount) as amount FROM public.pagado
            group by inv_id;
            SELECT * FROM pagado_por_factura;"""

        self._cr.execute(q_view_payments_invoices)

        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end

        var_date_type_ctrl = ''
        query_filter_provider = ''
        query_extra_invoices = ''
        if i.date_type == 'fecha_pago':
            var_date_type_ctrl = 'pagado.fechax'
        if i.provider_type == 'todo':
            query_filter_provider = ''
            query_extra_invoices = ''
        if i.provider_type == 'productor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.lotes.id_partner =  {i.productor_id.id} '
        if i.provider_type == 'emisor':
            query_extra_invoices = f' and account_move.partner_id = {i.productor_id.id}'
            query_filter_provider = f' and public.account_move.partner_id =  {i.productor_id.id} '

        # Aun no lo utilizo preguntar como sacariamos los anticipos y facturas adicionales
        q_pagado = f"""select public.res_partner.name,
                   case when account_move.total_impuestos_retenidos > 0 then (lotes_account_move_line.abono_kilogramos * lotes.precio_u) - 
                   ((lotes_account_move_line.abono_kilogramos * lotes.precio_u) * (0.0125)) 
                   else (lotes_account_move_line.abono_kilogramos * lotes.precio_u) end::numeric as importe_pagado,
                   lotes.name as lote,
                   lotes_account_move_line.uuid as uuid,
                   huertas.name as sader
                   FROM public.lotes_account_move_line
                   left join public.lotes on public.lotes_account_move_line.name = public.lotes.id
                   left join public.account_move on public.lotes_account_move_line.data_rel = public.account_move.id
                   left join public.res_partner on public.account_move.partner_id = public.res_partner.id
                   left join public.pagado_por_factura on public.lotes_account_move_line.data_rel = public.pagado_por_factura.inv_id
                   left join public.pagado on public.lotes_account_move_line.data_rel = public.pagado.inv_id
                   left join public.huertas on public.lotes.sader = public.huertas.id 
                   where public.account_move.amount_residual = 0
                   {query_filter_provider}
                   and public.{var_date_type_ctrl}  between '{i.date_start}' and '{i.date_end}'
                   union all            
                   SELECT res_partner.name,
                   sum(pagado_por_factura.amount)::numeric as amount,
                   null as lote,
                   account_move.uuid,
                   null as sader
                   FROM account_move 
                   left join pagado on account_move.id = pagado.inv_id 
                   left join res_partner on account_move.partner_id = res_partner.id
                   left join pagado_por_factura on account_move.id = pagado_por_factura.inv_id                    
                   WHERE NOT exists
                   (SELECT data_rel
                   FROM lotes_account_move_line p
                   WHERE p.data_rel = account_move.id)
                   and account_move.move_type = 'in_invoice'
                   and account_move.payment_state = 'paid'
                   and {var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
                   {query_extra_invoices}
                   group by res_partner.name,account_move.uuid
                   order by name
        """

        self._cr.execute(q_pagado)

        res_q_pagado = self._cr.fetchall()

        print(res_q_pagado)

        for lnxx in res_q_pagado:
            vals.append({'name': lnxx[0],
                         'importe_pagado': lnxx[1],
                         'lote':lnxx[2],
                         'uuid':lnxx[3],
                         'sader':lnxx[4]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }

#Pagado


class NfacnopagFacnopag(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.fac_no_pag_no_fac_no_pag'
    _description = 'Reporte de facturado no pagado y no facturado no pagado (Productores) MIX'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.date_start
            i.date_end
            i.date_type
        var_date_type_ctrl = ''
        if i.date_type == 'fecha_factura':
            var_date_type_ctrl = 'account_move.date'
        if i.date_type == 'fecha_lote':
            var_date_type_ctrl = 'lotes.fecha'


        vals = []
        # Creacion de primera vista#
        query_create_view_no_facturado_no_pagado = f"""CREATE OR REPLACE VIEW public.no_facturado_no_pagado
        AS select res_partner.name, sum(lotes.importe) as importe from public.lotes
        left join lotes_account_move_line on lotes.id = lotes_account_move_line.name
        left join res_partner on lotes.id_partner = res_partner.id
        left join account_move on lotes_account_move_line.data_rel = account_move.id 
        where lotes_account_move_line.data_rel is null
        and 
        {var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
        group by res_partner.name """

        self._cr.execute(query_create_view_no_facturado_no_pagado)

        #res_query_create_view_no_facturado_no_pagado = self._cr.fetchall()

        #Creacion de segunda vista#

        query_create_view_facturado_no_pagado = f"""CREATE OR REPLACE VIEW public.facturado_no_pagado
        AS SELECT res_partner.name,
        sum(case when account_move.total_impuestos_retenidos > 0 then
        (lotes_account_move_line.abono_kilogramos * lotes.precio_u) - ((lotes_account_move_line.abono_kilogramos * lotes.precio_u) * (0.0125))
        else (lotes_account_move_line.abono_kilogramos * lotes.precio_u) end)::numeric as importe
        FROM lotes_account_move_line
        LEFT JOIN lotes ON lotes_account_move_line.name = lotes.id
        LEFT JOIN account_move ON lotes_account_move_line.data_rel = account_move.id
        LEFT JOIN res_partner ON account_move.partner_id = res_partner.id
        WHERE account_move.amount_residual > 0::numeric
        and public.{var_date_type_ctrl} between '{i.date_start}' and '{i.date_end}'
        GROUP BY res_partner.name;"""

        self._cr.execute(query_create_view_facturado_no_pagado)

        #res_query_create_view_facturado_no_pagado = self._cr.fetchall()

        query = """select NAME, sum(importe) as importe from (
                   select name as NAME,importe FROM public.facturado_no_pagado
                   union all
                   select name as NAME,importe from public.no_facturado_no_pagado
                   order by name asc
                   ) x
                   group by NAME
                     """

        self._cr.execute(query)

        result = self._cr.fetchall()

        print(result)

        for l in result:
            vals.append({'NAME': l[0],
                         'importe': l[1]})

        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'date_start': i.date_start,
            'date_end': i.date_end,
        }

class PresupuestoXFactura(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.presupuesto_por_factura'
    _description = 'Reporte de presupuesto por factura PDF'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('Query')
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            i.date_type
        date_start_val = i.date_start
        date_end_val = i.date_end
        vals = []
        # Creacion de primera vista#

        query = f"""
        select distinct(data_rel) as id,
        account_move.uuid as uuid,
        res_partner.name as name,
        case when  sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed) < 0 then 
        (case when  sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed) = 0
        then (select amount from pagado_por_factura where inv_id = data_rel) else sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed)
        end) * -1 else (case when  sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed) = 0
        then (select amount from pagado_por_factura where inv_id = data_rel) else sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed)
        end) end as amount_residual_signed
        from lotes_account_move_line
        left join account_move on lotes_account_move_line.data_rel = account_move.id
        left join res_partner on account_move.partner_id = res_partner.id
        where lotes_presupuestos_rel = {i.presupuesto.id}
        group by data_rel,account_move.uuid,res_partner.id 
        union all
        SELECT account_move.id,
        account_move.uuid as uuid,
        res_partner.name as name,
        case when  sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed) < 0 then 
        (case when  sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed) = 0
        then (select amount from pagado_por_factura where inv_id = account_move.id) else sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed)
        end) * -1 else (case when  sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed) = 0
        then (select amount from pagado_por_factura where inv_id = account_move.id) else sum(account_move.amount_residual_signed)/count(account_move.amount_residual_signed)
        end) end as amount_residual_signed
        FROM public.account_move
        left join res_partner on account_move.partner_id = res_partner.id
        where presupuesto_lote_fac_adic_rel = {i.presupuesto.id}
        group by account_move.id,account_move.uuid,res_partner.id
        order by id asc
        """

        self._cr.execute(query)

        result = self._cr.fetchall()

        print(result)

        for l in result:
            vals.append({'id': l[0],
                         'uuid': l[1],
                         'name':l[2],
                         'amount_residual_signed':l[3],
                         'date_initial':i.date_start,})
        print('respuesta')
        print(date_start_val)
        today = datetime.now()
        dt_string = today.strftime("%d/%m/%Y %H:%M:%S")
        dt_print = "DT:", dt_string
        return {

            'doc_ids': docs_ids,
            'vals': vals,
            'presupuesto': i.presupuesto.name,
            'datetime': dt_print,
        }


"""    #INTEGRAR DATOS A UN ONE2MANY
        for recx in self:
            linesx = []
            for linez in recx.presupuestos_rel.lotes_provisionados:
                print(linez.id_pago)
                linesx.append((4, int(linez.id_pago)))
            print("lines", linesx)
"""
class ReporteFleterosPdf(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.lotes_fleteros'
    _description = 'Reporte Fleteros PDF'

    @api.model
    def _get_report_values(self, docs_ids, data=None):
        print('PRUEBA ALEXIS')
        print('Query')
        rango_fechas = self.env['reportes_saldos_wizard']
        for i in rango_fechas.search([], order='id desc', limit=1):
            i.date_type
        date_start_val = i.date_start
        date_end_val = i.date_end
        vals = []
        # Creacion de primera vista#

        query_create_fleteros_view = f"""
        CREATE OR REPLACE VIEW public.fleteros
        AS SELECT c.name AS id_flete,
        c.fecha,
        h.name AS huerta,
        c.municipio,
        c.cajas_mixtos_fletes AS cajas_camion,
        h.name AS nombre_transportista,
        c.importe_mas_retencion AS total,
        n.name AS beneficiario
        FROM fletes_modelo_tts c
        LEFT JOIN huertas h ON h.id = c.huerta
        LEFT JOIN res_partner x ON x.id = c.nombre_transportista
        LEFT JOIN res_partner n ON n.id = c.beneficiario
        WHERE fecha BETWEEN '{i.date_start}' AND '{i.date_end}'
        ORDER BY n.name;
        """
        self._cr.execute(query_create_fleteros_view)
        query_create_second_view_fleteros_2 = f"""
        SELECT  beneficiario,id_flete,fecha,huerta,municipio,cajas_camion,nombre_transportista,total,tot
        FROM    (
         SELECT fleteros.beneficiario,fleteros.id_flete, fleteros.fecha,huerta,fleteros.municipio,fleteros.cajas_camion,fleteros.nombre_transportista,fleteros.total,coalesce(cast(SUM(fleteros.total) as VARCHAR(20))) as tot
         FROM   public.fleteros
         GROUP by ROLLUP (BENEFICIARIO
               ,id_flete
               ,fecha
               ,huerta
               ,municipio
               ,cajas_camion
               ,nombre_transportista
               ,TOTAL)
               order by Id_flete DESC
        ) AS X
        WHERE   BENEFICIARIO IS NOT null
        AND (
             (
              Id_flete IS NOT NULL
              AND Fecha IS NOT null
              and Total is not null
              and Huerta is not null
              and Municipio is not null
              and Cajas_camion is not null
              and Nombre_transportista is not null
             )
             OR (
                 Id_Flete IS NULL
                 AND fecha IS null
                 and total is  null
                 and huerta is null
                 and municipio is null
                 and cajas_camion is null
                 and nombre_transportista is null
                )
            )
            order by Id_flete DESC
        """



        self._cr.execute(query_create_second_view_fleteros_2)
        result = self._cr.fetchall()
        print('Prueba')
        print(result)

        for l in result:
            vals.append({'beneficiario': l[0],
                         'id_flete': l[1],
                         'fecha':l[2],
                         'huerta':l[3],
                         'municipio':l[4],
                         'cajas_camion':l[5],
                         'nombre_transportista':l[6],
                         'tot':l[8],})
        print('respuesta')
        print(date_start_val)
        today = datetime.now()
        dt_string = today.strftime("%d/%m/%Y %H:%M:%S")
        dt_print = "DT:", dt_string
        return {

            'doc_ids': docs_ids,
            'vals': vals,
        }