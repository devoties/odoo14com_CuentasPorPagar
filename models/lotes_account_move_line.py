# -*- coding:utf-8 -*-how save many2many custom more data
from datetime import datetime
from time import strftime

from odoo import fields, models, api
import pandas as pd
from datetime import date,timedelta

class LotesCfdi(models.Model):
    _name = "lotes_account_move_line"
    _description = "Linea de factura con lotes"
    name = fields.Many2one(comodel_name='lotes',string='Lote')
    lotes_fecha_recepcion = fields.Date(string='Fecha Recepcion',related='name.fecha')
    lotes_nombre_productor = fields.Many2one(related='name.id_partner')
    lotes_huerta = fields.Many2one(related='name.sader')
    abono_kilogramos = fields.Float(string='Abono Kg')
#este es compute
    abono_importe = fields.Float(string='Abono Importe',compute='_compute_abono_importe')
    lotes_saldo_pendiente = fields.Float(string='Importe pendiente',related='name.saldo_pendiente',compute='_compute_kg_pendientes')
#este es compute
    lotes_kilogramos_pendiente = fields.Float(string='Kg Pendientes',related='name.kilogramos_pendientes',store=True,compute='_compute_kg_pendientes')
    metodo_pago = fields.Char(related='data_rel.metodo_pago')
    forma_de_pago = fields.Char(related='data_rel.forma_de_pago')
    lotes_kilogramos = fields.Float(string='Kilogramos Lote',related='name.cantidad',compute='_compute_kg_pendientes')
    lotes_importe = fields.Float(string='Importe Lote',related='name.importe')
    lotes_sader = fields.Many2one(string='Sader',related='name.sader')
    lotes_sader_code = fields.Char(string='Sader Codigo', related='name.sader.sader')
    lotes_jefe_acopio = fields.Many2one(string='Jefe Acopio', related='name.jefe_acopio')
    #verificar_contrato
    lotes_sader_contrato = fields.One2many(string='Contratos', related='name.sader.contrato_terceros_lista')
    lotes_precio_unitario = fields.Float(string='Precio Unitario Lote',related='name.precio_u')
    lotes_observaciones = fields.Char(string='Observaciones',related='name.observaciones')
    cfdi_id_rel = fields.Many2one(string='Cfdi',comodel_name='account.move')
    lotes_id_rel = fields.Many2one(string='Lotes id Rel', comodel_name='lotes')
    status_pago_rel = fields.Char(string='Estatus Pago',related='name.status_pago')
    data_rel = fields.Many2one(comodel_name='account.move',string='Data Rel',index=True,required=True,readonly=True, auto_join=True, ondelete="cascade",_rec_name='uuid')
    serie = fields.Char(related='data_rel.serie')
    folio = fields.Char(related='data_rel.folio')
    uuid = fields.Char(related='data_rel.uuid')
    id_partner = fields.Many2one(related='data_rel.partner_id',string='Emisor de factura')
    fecha_factura = fields.Date(related='data_rel.invoice_date',string='Fecha Factura')
    fecha_pago = fields.Date(related='data_rel.invoice_date_due',string='Fecha De Vencimiento')
    estado_pago = fields.Selection(related='data_rel.state',string='Estado Factura')
    estado_factura = fields.Selection(related='data_rel.payment_state',string='Estado Pago')
    estado_contabilizacion = fields.Selection(string='Estado Contabilizacion',related='name.state')
    provision_lote = fields.Char(string='Provision Lote',related='name.status_provision',stored=True,readonly=True)
    impuesto = fields.Char(string='Retencion',compute='calcularCampos_Impuestos')
    abono_importe_con_impuesto = fields.Float(string='Abono Importe + Ret',compute='calcularCampos_Impuestos')
    estatus_contratos = fields.Char(string='Etatus Contrato',compute='get_contracts_data')
    es_tarjeta_apeam = fields.Boolean(string='Tarjeta Apeam',compute='get_documental_data')
    es_opinion = fields.Char(string='OPINION',compute='get_aditional_data')
    es_ine = fields.Boolean(string='INE',compute='get_aditional_data')
    es_cif = fields.Char(string='CIF',compute='get_aditional_data')
    estatus_layout = fields.Char(string='Estatus Layout')


    #trae los datos documentales del proveedor a traves de la relacion factura "data_rel"
    def get_aditional_data(self):
        for line in self:
            #calcula las opiniones que estan el rango de fecha de la factura relacionada "data_rel"
            x = line.env['opinion_cumplimiento_sat'].search([('opinion_cumplimiento_partner_rel','=',line.data_rel.partner_id.id)]).mapped("fecha_emision")
            fecha_factura = pd.to_datetime(line.data_rel.invoice_date)
            mes_factura = fecha_factura.strftime('%b')
            contador_vigencias = 0
            status = ''
            for linx in x:
                mes_contrato = linx.strftime('%b')
                print('Diferencia')
                print((fecha_factura-linx).days)
                if mes_factura == mes_contrato or int(((fecha_factura-linx).days)) < 0 or int(((fecha_factura-linx).days)) <= (90):
                    contador_vigencias = contador_vigencias + 1
                    if contador_vigencias == 0:
                        status = 'VENCIDO'
                    if contador_vigencias > 0:
                        status = 'VIGENTE'

                else:
                    contador_vigencias = contador_vigencias + 0
                    if contador_vigencias == 0:
                        status = 'VENCIDO'
                    if contador_vigencias > 0:
                        status = 'VIGENTE'
            line.es_opinion = status

            #calcula qty de ines vigentes o vencidas
            calcular_ines = line.env['ine_sat'].search_count([('ine_partner_rel','=',line.data_rel.partner_id.id)])
            if calcular_ines >= 1:
                line.es_ine = True
            if calcular_ines < 1:
                line.es_ine = False
            #calcula las caratulas que estan el rango de fecha de la factura relacionada "data_rel"
            qty_cifs = line.env['cif'].search([('cif_rel', '=', line.data_rel.partner_id.id)]).mapped('fecha_emision')
            fecha_factura = pd.to_datetime(line.data_rel.invoice_date)
            mes_factura = fecha_factura.strftime('%b')
            contador_vigencias = 0
            status = ''
            for linx in qty_cifs:
                mes_contrato = linx.strftime('%b')
                print('Otro parametro que ocupo ver')
                print(mes_contrato)
                if mes_factura == mes_contrato or int(((fecha_factura-linx).days)) < 0 or int(((fecha_factura-linx).days)) <= (90):
                    contador_vigencias = contador_vigencias + 1
                    if contador_vigencias == 0:
                        status = 'VENCIDO'
                    if contador_vigencias > 0:
                        status = 'VIGENTE'

                else:
                    contador_vigencias = contador_vigencias + 0
                    if contador_vigencias == 0:
                        status = 'VENCIDO'
                    if contador_vigencias > 0:
                        status = 'VIGENTE'
            line.es_cif = status


    def get_documental_data(self):
        for line in self:
            #Busca la tarjeta APEAM
            line.es_tarjeta_apeam = line.env["huertas"].search([('id', '=', line.name.sader.id)]).es_tarjeta_apeam
            #Busca la OPINION DE CUMPLIMIENTO


    def get_contracts_data(self):
        for line in self:
            busqueda_vigencias = line.env["huertas_contratos_terceros"].search_count([('huertas_contratos_terceros_huertas_rel', '=', line.name.sader.id),('fecha_vencimiento','>=',date.today())])
            x = line.env["huertas_contratos_terceros"].search(
                [('huertas_contratos_terceros_huertas_rel', '=', line.name.sader.id),
                 ('fecha_vencimiento', '>=', date.today())])
            print('****busqueda vigencias******')
            print(busqueda_vigencias)
            print('**********Contador de lista beneficiarios************')
            validator_count = 0
            for lnx in x:
                for lnx_benef in lnx.beneficiarios:
                    if lnx_benef.id == line.data_rel.partner_id.id:
                        validator_count = validator_count + 1
                    if lnx_benef.id != line.data_rel.partner_id.id:
                        validator_count = validator_count + 0
            print(validator_count)

            if busqueda_vigencias <= 0:
               line.estatus_contratos = 'VENCIDO'
            if busqueda_vigencias > 0:
                if validator_count > 0:
                   line.estatus_contratos = 'VIGENTE'
                else:
                    line.estatus_contratos = 'VENCIDO'


    def name_get(self):
        result = []
        for record in self:
            record_name = f'{record.uuid} \n {record.id_partner.name} \n {record.serie} \n {record.folio} \n {record.fecha_factura} \n {record.estado_pago}'
            result.append((record.id, record_name))
        return result


    def contabilizar_lote(self):
        for line in self:
         line.name.state = 'Contabilizado Lote'

    def contabilizar_cfdi(self):
        for line in self:
         line.name.state = 'Contabilizado Cfdi'


    def convertir_a_borrador(self):
        for line in self:
         line.name.state = 'borrador'

    #es para cuando recien selecciona el lote (calculo inicial)
    @api.onchange('name')
    @api.depends('name')
    def _compute_kg_pendientes(self):

       # recorro todos los datos de la funcion
       for lote in self:

        #suma de abono de kilogramos
        records_sum = sum(lote.env["lotes_account_move_line"].search([('name','=',lote.name.id)]).mapped('abono_kilogramos'))
        kilogramos_pendientes = sum(lote.env["lotes_account_move_line"].search([('name','=',lote.name.id)]).mapped('lotes_kilogramos_pendiente'))

        lote.abono_kilogramos = lote.lotes_kilogramos - records_sum

        lote.lotes_kilogramos_pendiente = lote.lotes_kilogramos - records_sum
        lote.lotes_saldo_pendiente = lote.lotes_kilogramos_pendiente * lote.lotes_precio_unitario


    #este esta bien
    @api.onchange('abono_kilogramos')
    def _compute_abono_importe(self):
       for lote in self:
        # campo abono importe compute
        records_sum = 0

        records_sum = sum(lote.env["lotes_account_move_line"].search([('name','=',lote.name.id)]).mapped('abono_kilogramos'))

        if records_sum == lote.lotes_kilogramos:
            lote.lotes_kilogramos_pendiente = 0
            lote.lotes_saldo_pendiente = 0
            lote.abono_importe = lote.abono_kilogramos * lote.lotes_precio_unitario
        if records_sum < lote.lotes_kilogramos:
            lote.lotes_kilogramos_pendiente = (lote.lotes_kilogramos - records_sum) - (lote.abono_kilogramos)
            lote.lotes_saldo_pendiente = lote.lotes_kilogramos_pendiente * lote.lotes_precio_unitario
            lote.abono_importe = lote.abono_kilogramos * lote.lotes_precio_unitario






    @api.depends('impuesto','abono_importe_con_impuesto','data_rel')
    def calcularCampos_Impuestos(self):
        for line in self:
            #Agregar resultado nulo por si el dato no existe
            amount_untaxed_calc = 0.0
            amount_total_calc = 0.0


            if line.data_rel.id:
                #print('SI EXISTE RELACION')
                amount_untaxed_calc = sum(line.env["account.move"].search([('id', '=', line.data_rel.id)]).mapped('amount_untaxed'))
                amount_total_calc = sum(line.env["account.move"].search([('id', '=', line.data_rel.id)]).mapped('amount_total'))

            if not line.data_rel.id:
                #print('NO EXISTE RELACION')
                amount_untaxed_calc = 0.0
                amount_total_calc = 0.0
            #print(amount_total_calc)
            #print(amount_untaxed_calc)
            ref_impuesto = ''
            abono_importe_calc = 0.0

            if amount_total_calc is None:
                ref_impuesto = ''
                abono_importe_calc = 0
            if  amount_untaxed_calc is None:
                ref_impuesto = ''
                abono_importe_calc = 0
            if amount_total_calc != amount_untaxed_calc:
                ref_impuesto = 'ISR 1.25%'
                abono_importe_calc = (line.abono_importe) - (line.abono_importe * 0.0125)
            if amount_total_calc == amount_untaxed_calc:
                ref_impuesto = 'TASA 0'
                abono_importe_calc = line.abono_importe

            line.impuesto = ref_impuesto
            line.abono_importe_con_impuesto = abono_importe_calc








