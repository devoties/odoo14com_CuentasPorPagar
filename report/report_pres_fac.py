# -*- coding:utf-8 -*-

from odoo import fields, models, api
#Listo
class PresupuestoFacExcel(models.AbstractModel):
    _name = 'report.cuentas_por_pagar.pres_fac_xls'
    _description = 'Reporte Presupuesto Por Factura (Productores)'
    _inherit = ['report.report_xlsx.abstract']

    @api.model
    def generate_xlsx_report(self, workbook, data,row_count):

        for i in self.env['reportes_saldos_wizard'].search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.presupuesto
        print('id_presupuesto')
        print(i.presupuesto.id)
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
        print('Ressssss')
        print(result)
        row_count = 0
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 10, 'align': 'vcenter', })
        sheet = workbook.add_worksheet('Reporte 1')
        for lines in result:
            row_count = row_count + 1
            sheet.set_column(3, 3, 50)
            sheet.set_column(2, 2, 30)
            sheet.write(0, 0, 'Id', format1)
            sheet.write(row_count, 0, lines[0], format2)
            sheet.write(0, 1, 'Uuid', format1)
            sheet.write(row_count, 1, lines[1], format2)
            sheet.write(0, 2, 'Proveedor', format1)
            sheet.write(row_count, 2, lines[2], format2)
            sheet.write(0, 3, 'Importe', format1)
            sheet.write(row_count, 3, lines[3], format2)