# -*- coding:utf-8 -*-
import requests

from odoo import fields, models, api
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, Session
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import Integer, String, Float, SmallInteger, Numeric, DateTime, Date
from sqlalchemy import distinct
import logging
import pandas as pd
from datetime import date,timedelta

_logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

Base = declarative_base()

#Clase de movimientos de recepcion
class CortesData(Base):
    __tablename__ = 'ZZZ_RecepcionLotes6'
    id_acuerdo = Column('IdAcuerdo', Integer())
    id_orden_corte = Column('IdOrdenCorte', Integer())
    id_lote_recepcion = Column('IdLoteRecepcion', Integer(), primary_key=True)
    nombre_productor = Column('Nombre', String(500))
    huerta = Column('Huerta',String(500))
    sader = Column('NoRegistro',String(500))
    fecha = Column('Fecha',DateTime)
    poblacion = Column('Poblacion', String(500))
    tipo_corte = Column('TipoCorte', String(500))
    precio = Column('Precio',Float)
    transportista = Column('Expr2', String(500))
    empresa_corte = Column('Expr3', String(500))
    jefe_acopio = Column('Expr4',String(200))
    candado = Column('Candado',String(200))
    cajas_entregadas = Column('CajasCortadas',Integer())
    cajas_entregadas_mixto = Column('CajasMixto', Integer())
    peso_neto = Column('PesoNeto',Float)
    peso_productor = Column('PesoBasculaProductor',Float)
    bico = Column('COPREF',String(200))
    ticket = Column('Ticket', String(200))
    id_productor = Column('IdProductor',Integer())
    id_jefe_cuadrilla = Column('IdJefeCuadrilla',Integer())
    id_lote = Column('IdLote',Integer())
    tipo_corte_2 = Column('Tipocorte2',String(20))
    peso_nuevo_productor = Column('PesoNuevoProductor',Float)
#Clase de movimientos de recepcion para proveedor
class CorteCatData(Base):
  #  __table_args__ = {'extend_existing': True}
    __tablename__ = 'ODOO_CuentasPorPagarCorteCatalogoProveedores'
    id_lote_recepcion = Column('IdLoteRecepcion',Integer(), primary_key=True)
    fecha = Column('Fecha', DateTime)
    empresa_corte = Column('Expr3', String(500))
    id_jefe_cuadrilla = Column('IdJefeCuadrilla',Integer())
    id_productor = Column('IdProductor',Integer())

#Clase de movimientos de recepcion para huertos
class CorteCatHuertasData(Base):
    #  __table_args__ = {'extend_existing': True}
    __tablename__ = 'ODOO_CuentasPorPagarCorteCatalogoHuertas'
    id_lote_recepcion = Column('IdLoteRecepcion', Integer(), primary_key=True)
    huerta = Column('huerta', String(500))
    sader = Column('NoRegistro',String(500))
    id_productor = Column('IdProductor',Integer())
    fecha = Column('Fecha', DateTime)

#Clase de movimientos de recepcion para Productores
class CorteCatProductorData(Base):
    __tablename__ = 'ODOO_CuentasPorPagarCorteCatalogoProductores'
    id_lote_recepcion = Column('IdLoteRecepcion', Integer(), primary_key=True)
    nombre = Column('Nombre', String(500))
    id_productor = Column('IdProductor',Integer())
    fecha = Column('Fecha', DateTime)

#Clase de movimientos de recepcion para jefe de acopio
class CorteCatJefeAcopioData(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'ODOO_CuentasPorPagarCorteCatalogoProveedores'
    id_lote_recepcion = Column('IdLoteRecepcion', Integer(), primary_key=True)
    nombre = Column('Expr4', String(500))
    fecha = Column('Fecha', DateTime)

class Session():
    def session(engine):
        Session = sessionmaker(bind=engine)
        # session = Session()
        session = scoped_session(Session)

        return session

    def engine():
        server_addres = '192.168.88.214' + ":" + "49703"
        #server_addres = 'e3210dfde5c7.sn.mynetname.net' + ":" + "49703"
        database = 'TTS'
        username = 'sa'
        password = 'HideMyPassBm123*'

        arguments = dict(server=server_addres, user=username,
                         password=password, database=database, charset="utf8")

        engine = sa.create_engine('mssql+pymssql:///', connect_args=arguments)
        return engine

    # Modelo de odoo


class Cortes(models.Model):
    _name = "cortes"
    _inherit=['mail.thread','mail.activity.mixin','portal.mixin']
    _description = 'Cortes Module'
    # reestriccion por db para id del lote type_unique=(name)
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Datos duplicados en el rango solicitado, revisa tu rango')]

#    @api.constrains('name')
 #   def _name_valid(self):

  #          raise exceptions.ValidationError("Datos duplicados en el rango solicitado, revisa tu rango")

    name = fields.Integer(string='Id Lote Recepcion')

    id_acuerdo = fields.Integer(string='Id Acuerdo')

    id_orden_corte = fields.Integer(string='Id Orden Corte')

    nombre_productor = fields.Many2one(string='Nombre del productor',comodel_name='res.partner')

    huerta = fields.Char(string='Huerta')

    sader = fields.Many2one(String='Sader',comodel_name='huertas')

    fecha = fields.Datetime(String='Fecha')

    poblacion = fields.Char(string='Poblacion')

    tipo_corte = fields.Char(string='Tipo De Corte')

    transportista = fields.Char(string='Trasnportista')

    empresa_corte = fields.Many2one(string='Empresa de corte', comodel_name='res.partner')

    jefe_acopio = fields.Many2one(string='Jefe Acopio',comodel_name='res.partner')

    candado = fields.Char(string='Candado')

    cajas_entregadas = fields.Integer(string='Cajas Cortadas')

    peso_neto = fields.Float(string='Peso Neto')

    peso_productor = fields.Float(string='Peso Productor')

    bico = fields.Char(string='Bico')

    ticket = fields.Char(string='Ticket')

    active = fields.Boolean(string='Activo', default=True)

    #campo one2many apunta al campo many2one de cuadrillas para relacionar los campos
    cuadrilla = fields.One2many('cuadrillas','cuadrilla_rel',string='Cuadrillas')

    id_productor = fields.Integer(string='Id Productor')

    id_jefe_cuadrilla = fields.Integer(string='Id Jefe Cuadrilla')

    kilogramos_ajuste = fields.Float(string='Kilogramos de ajuste')

    total_ajuste = fields.Float(string='Total Ajuste',compute='importe_ajuste')

    total_importe = fields.Float(string='Importe',compute='total_cuadrillas')

    id_lote = fields.Integer(string='Id Lote')

    tipo_corte_2 = fields.Char(string='Tipo Corte 2')

    peso_nuevo_productor = fields.Float(string='Peso Nuevo Productor')
    peso_productor_lote = fields.Float(string='Peso bascula')

    cuadrilla_extra = fields.Float(string='View cuadrilla extra', compute='view_cuadrilla_extra')

    account_move_cortes_rel = fields.Many2one(comodel_name='account.move')

    peso_promedio_cajas_corte = fields.Float(string='Promedio cajas')
    peso_promedio_cajas_corte2 = fields.Float(string='Promedio cajas', compute='_promedio_cajas_corte')

    state_alert_corte = fields.Selection(selection=[('alerta_exeso', 'Exceso'), ('alerta_faltante', 'Faltante'),
                                        ('margen', 'margen'), ('bloqueo', 'Bloqueo')]
                             , default='margen', string='Estados', copy=False, )

    data_rel = fields.Many2one(comodel_name='account.move', string='Data Rel', index=True, required=True,
                               auto_join=True, ondelete="cascade", _rec_name='uuid')
    uuid = fields.Char(related='data_rel.uuid', store=True)
    ine_venc = fields.Char(string='INE VENC', compute='get_ine')
    es_opinion = fields.Char(string='OPINION', compute='get_aditional_data')
    fecha_factura = fields.Date(related='data_rel.invoice_date', string='Fecha Factura')
    fecha_pago = fields.Date(related='data_rel.invoice_date_due', string='Fecha De Vencimiento')
    es_ine = fields.Boolean(string='INE', compute='get_aditional_data')
    es_cif = fields.Char(string='CSF', compute='get_aditional_data')
    estatus_contratos = fields.Char(string='Etatus Contrato', compute='get_contracts_data')
    lotes_nombre_productor = fields.Many2one(related='name2.id_partner')
    name2 = fields.Many2one(comodel_name='lotes', string='Lote')
    id_partner = fields.Many2one(related='data_rel.partner_id', string='Emisor de factura', store=True)
    serie = fields.Char(related='data_rel.serie')
    folio = fields.Char(related='data_rel.folio')
    estado_pago = fields.Selection(related='data_rel.state', string='Estado Factura')
    estado_factura = fields.Selection(related='data_rel.payment_state', string='Estado Pago')

    testeo3 = fields.Many2many(comodel_name='tarifas_fletes', string='FLETES TESTEO')


    def get_contracts_data(self):
        for line in self:
            busqueda_vigencias = line.env["huertas_contratos_terceros"].search_count([('huertas_contratos_terceros_huertas_rel', '=', line.name.sader.id),('fecha_vencimiento','>=',line.lotes_fecha_recepcion),
                                                                                      ('fecha_apertura','<=',line.lotes_fecha_recepcion)])
            x = line.env["huertas_contratos_terceros"].search(
                [('huertas_contratos_terceros_huertas_rel', '=', line.name.sader.id),
                 ('fecha_vencimiento', '>=', line.lotes_fecha_recepcion),
                 ('fecha_apertura','<=',line.lotes_fecha_recepcion)])
            print('****busqueda vigencias******')
            print(busqueda_vigencias)
            print('**********Contador de lista beneficiarios************')
            validator_count = 0

    def get_aditional_data(self):
        for line in self:
            # calcula las opiniones que estan el rango de fecha de la factura relacionada "data_rel"
            x = line.env['opinion_cumplimiento_sat'].search(
                [('opinion_cumplimiento_partner_rel', '=', line.data_rel.partner_id.id)]).mapped("fecha_emision")
            if line.data_rel.invoice_date is not False:
                fecha_factura = pd.to_datetime(line.data_rel.invoice_date)
                print('tes 1')
                mes_factura = fecha_factura.strftime('%b')
                contador_vigencias = 0
                status = ''
                for linx in x:
                    mes_contrato = linx.strftime('%b')
                    print('Diferencia')
                    diff = int((pd.to_datetime(fecha_factura) - pd.to_datetime(linx)).days)
                    print(diff)
                    if mes_factura == mes_contrato or diff < 0 or diff <= (90):
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

                # calcula qty de ines vigentes o vencidas
                calcular_ines = line.env['ine_sat'].search_count(
                    [('ine_partner_rel', '=', line.data_rel.partner_id.id)])
                if calcular_ines >= 1:
                    line.es_ine = True
                if calcular_ines < 1:
                    line.es_ine = False
                # calcula las caratulas que estan el rango de fecha de la factura relacionada "data_rel"
                qty_cifs = line.env['cif'].search([('cif_rel', '=', line.data_rel.partner_id.id)]).mapped(
                    'fecha_emision')
                fecha_factura = pd.to_datetime(line.data_rel.invoice_date)
                mes_factura = fecha_factura.strftime('%b')
                contador_vigencias = 0
                status = ''
                for linx in qty_cifs:
                    mes_contrato = linx
                    mes_contrato = mes_contrato.strftime('%b')
                    print('Otro parametro que ocupo ver')
                    print(mes_contrato)
                    print('Diferencia')
                    diff = int((pd.to_datetime(fecha_factura) - pd.to_datetime(linx)).days)
                    print(diff)
                    if mes_factura == mes_contrato or diff < 0 or diff <= (90):
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
            else:
                line.es_opinion = 'VIGENTE'
                line.es_cif = 'VENCIDO'
                line.estatus_contratos = 'VIGENTE'



    def name_get(self):
        result = []
        for record in self:
            record_name = f'{record.uuid} \n {record.id_partner.name} \n {record.serie} \n {record.folio} \n {record.fecha_factura} \n {record.estado_pago}'
            result.append((record.id, record_name))
        return result

    def get_ine(self):
        for l in self:
            #contador en 0's
            contador = 0
            #mapeo el modelo en un objeto
            ines_vigentes = l.env['ine_sat']
            # variable de control para fecha
            var_control_date = ''
            if l.estado_factura == 'paid':
               var_control_date = l.fecha_pago_tuple
               var_control_date = var_control_date.replace('(', '')
               var_control_date = var_control_date.replace(')', '')
               var_control_date = var_control_date[0:10]
               if var_control_date.count('-') >= 3:
                  var_control_date = str(var_control_date[0:4])

            print(var_control_date)
            if l.estado_factura != 'paid':
                var_control_date = str(date.today())
            #Revisar resultados finales
            for i in ines_vigentes.search([('ine_partner_rel','=',l.data_rel.partner_id.id)], order='id desc'):
                format_date = str(i.fecha_vencimiento)
                if format_date[0:4] >= var_control_date[0:4] and i.fecha_vencimiento is not False:
                    contador = contador + 1
                else:
                    contador = contador + 0
            contador = contador
            if contador >= 1:
                l.ine_venc = 'VIGENTE'
            else:
                l.ine_venc = 'VENCIDO'

    @api.model
    def create(self, variables):
        if variables['peso_promedio_cajas_corte'] > 28:
            variables['state_alert_corte'] = 'alerta_exeso'
            #variables['alerta_peso_cajas'] = '***CAJAS CON MAS DE 28kg***'
        if variables['peso_promedio_cajas_corte'] < 22:
            variables['state_alert_corte'] = 'alerta_faltante'
            #variables['alerta_peso_cajas'] = '***CAJAS CON MENOS DE 22kg***'
        return super(Cortes, self).create(variables)

    def _promedio_cajas_corte(self):
        for rec_promedio in self:
            rec_promedio.peso_nuevo_productor = rec_promedio.peso_productor
            if rec_promedio.peso_nuevo_productor != 0.0:
                rec_promedio.peso_promedio_cajas_corte2 = rec_promedio.peso_nuevo_productor / rec_promedio.cajas_entregadas
                if rec_promedio.peso_promedio_cajas_corte2 > 28.0:
                    rec_promedio.state_alert_corte = 'alerta_exeso'
                if rec_promedio.peso_promedio_cajas_corte2 < 22.0:
                    rec_promedio.state_alert_corte = 'alerta_faltante'
            else:
                rec_promedio.peso_promedio_cajas_corte2 = 0.0

    def add_salida_falso(self):
        for linea in self:
            id_salida_falso = self.env['tipo_cuadrillas'].search([('name', '=', 'SALIDA EN FALSO')], limit=1)
            recordObjectAjuste = {'name': id_salida_falso.id,
                                  'cuadrilla_rel': linea.id,
                                  'importe': 3800, }
            insert_cuadrilla_normal = self.env['cuadrillas'].create(recordObjectAjuste)
            return True
    @api.depends('total_ajuste')
    def importe_ajuste(self):
        id_ajuste = self.env['tipo_cuadrillas'].search([('name', '=', 'AJUSTE')], limit=1)
        for line in self:
            records_sum = sum(self.env["cuadrillas"].search([('cuadrilla_rel.name', '=', line.name),('name','=',id_ajuste.id)]).mapped('importe'))*(-1)
            print(records_sum)
            line.total_ajuste = records_sum

    @api.depends('total_ajuste')
    def view_cuadrilla_extra(self):
        id_ajuste = self.env['tipo_cuadrillas'].search([('name', '=', 'CUADRILLA EXTRA')], limit=1)
        for line in self:
            records_sum = sum(self.env["cuadrillas"].search(
                [('cuadrilla_rel.name', '=', line.name), ('name', '=', id_ajuste.id)]).mapped('importe'))
            print(records_sum)
            line.cuadrilla_extra = records_sum


    def open_wizard_entrada_kilogramos(self):
        return {'type':'ir.actions.act_window',
                'res_model':'cuadrillas_kilogramos',
                'view_mode':'form',
                'target':'new'}

    @api.depends('total_importe')
    def total_cuadrillas(self):
        for line in self:
            records_sum = sum(line.env["cuadrillas"].search([('cuadrilla_rel.id', '=', line.id)]).mapped('importe'))
            line.total_importe = records_sum


    # calcula las cuadrillas extras y modifica las cuadrillas normales en caso de que las reglas lo requieran
    def calcularCuadrillasExtra(self):
        id = self.env['tipo_cuadrillas'].search([('name', '=', 'CUADRILLA EXTRA')], limit=1)
        id_cuadrilla_normal = self.env['tipo_cuadrillas'].search([('name', '=', 'CUADRILLA NORMAL')], limit=1)
        for linea in self:

            # calculador de tarifa de cuadrilla
            tarifa = 0
            tarifa_2 = 0
            cuadrilla_normal_search = self.env['cuadrillas'].search([('cuadrilla_rel', '=', linea.id),('name','=',id_cuadrilla_normal.id)], limit=1)
            print(cuadrilla_normal_search.id)
            cuadrilla_browse = self.env['cuadrillas'].browse([cuadrilla_normal_search.id])
            if cuadrilla_normal_search.id:

               if linea.peso_productor > 6000:
                  tarifa = 4800
                  tarifa_2 =  linea.peso_productor * 1.65
               if linea.peso_productor < 6000:
                  tarifa = 7500
                  tarifa_2 = 7500
               cuadrilla_browse.write({'importe': tarifa_2})
               self.env.cr.commit()
               print('Logger')
               print(tarifa_2)
            # objeto de datos obtenidos name = cuadrillas normal, cudrilla rel = el id que arrojara el almacenamiento
            # del objeto anterior de los cortes, importe = calculo de cuadrilla por Kilogramos
            recordObjectCuadrillasExtraPorCorte =    {'name': id.id,
                                                      'cuadrilla_rel': linea.id,
                                                      'importe': tarifa}
            insert_cuadrilla_normal = self.env['cuadrillas'].create(recordObjectCuadrillasExtraPorCorte)
            self.env.cr.commit()



    def download_data(self):

        engine = Session.engine()
        session = Session.session(engine)

        # valores globales para llamar el objeto fuera del modelo
        global cortes_object
        # ordenar por nombre
        # lote_inicial_object.search([],order='name')
        rango_cortes_obj = self.env['cortes_wizard']
        contactos_obj = self.env['res.partner']
        huertas_obj = self.env['huertas']
        productor_obj = self.env['res.partner']
        jefe_acopio_obj = self.env['res.partner']
        huerta_prod_obj = self.env['res.partner']

        for i in rango_cortes_obj.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.fecha_inicial
            i.fecha_final
        #Query que genera unico el catalogo de productores dependiendo del rango de lotes
        cortes_object_cat_empresa_corte = session.query(distinct(CorteCatData.id_jefe_cuadrilla),CorteCatData.empresa_corte).order_by(
                CorteCatData.empresa_corte).filter(CorteCatData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()
        cortes_object_cat_huertas = session.query(distinct(CorteCatHuertasData.sader),CorteCatHuertasData.huerta,CorteCatHuertasData.id_productor).order_by(
            CorteCatHuertasData.sader).filter(CorteCatHuertasData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()
        cortes_object_cat_productores = session.query(distinct(CorteCatProductorData.id_productor),CorteCatProductorData.nombre).order_by(
                CorteCatProductorData.nombre).filter(CorteCatProductorData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()
        cortes_object_cat_jefe_acopio = session.query(distinct(CorteCatJefeAcopioData.nombre)).order_by(
                CorteCatJefeAcopioData.nombre).filter(CorteCatJefeAcopioData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()


        #arreglo que recorre el objeto
        for record2 in cortes_object_cat_empresa_corte:
            #variable global para respuesta del query
            global response
            response = ''
            id_category_jefe_cuadrilla = self.env.ref('cuentas_por_pagar.category_corte')
            #agregar datos de al diccionario python
            response = {'id_jefe_cuadrilla': record2[0],
                        'name': record2[1],
                        'category_id': id_category_jefe_cuadrilla}
            if self.env['res.partner'].search_count([('id_jefe_cuadrilla', '=', record2[0])]) >= 1:
                print('Este contacto ya existe')
                print(self.env['res.partner'].search_count([('id_jefe_cuadrilla', '=', record2[0])]))
            if self.env['res.partner'].search_count([('id_jefe_cuadrilla', '=', record2[0])]) == 0:
                rec = self.env['res.partner'].create(response)
                self.env.cr.commit()
                print(response)

        for record4 in cortes_object_cat_productores:
                # variable global para respuesta del query
            global response3
            response3 = ''
            id_category_productor = self.env.ref('cuentas_por_pagar.category_productor')
                # agregar datos de al diccionario python
            response3 = {'name': record4[1],
                         'id_productor': record4[0],
                         'category_id': id_category_productor}
                # valida que no halla registros repetidos contado los registros coincidentes
            if self.env['res.partner'].search_count([('name', '=', record4[0])]) >= 1:
                    print('Este contacto ya existe')
                    print(self.env['res.partner'].search_count([('name', '=', record4[0])]))
                # valida y si no hay registros coincidentes almacena un nuevo registro
            if self.env['res.partner'].search_count([('name', '=', record4[0])]) == 0:
                    rec3 = self.env['res.partner'].create(response3)
                    self.env.cr.commit()
                    print(response3)




        for record3 in cortes_object_cat_huertas:
                # variable global para respuesta del query
            global response2
            response2 = ''
            for x in contactos_obj.search([('id_productor', '=', record3.id_productor)]):
             x.id
                # agregar datos de al diccionario python
            response2 = {'name': record3[1],
                         'sader': record3[0],
                          'productor':x.id}
                # valida que no halla registros repetidos contado los registros coincidentes
            if self.env['huertas'].search_count([('sader', '=', record3[0])]) >= 1:
                print('Este huerto ya existe')
                print(self.env['huertas'].search_count([('sader', '=', record3[0])]))
                # valida y si no hay registros coincidentes almacena un nuevo registro
            if self.env['huertas'].search_count([('sader', '=', record3[0])]) == 0:
                rec2 = self.env['huertas'].create(response2)
                self.env.cr.commit()
                print(response2)




        #agregar id jefe cuadrilla Modificar
        for record5 in cortes_object_cat_jefe_acopio:
                # variable global para respuesta del query
            global response4
            response4 = ''
            id_category_jefe_cuadrilla = self.env.ref('cuentas_por_pagar.category_jefe_acopio')
                # agregar datos de al diccionario python
            response4 = {'name': record5[0],
                         'category_id': id_category_jefe_cuadrilla}
                # valida que no halla registros repetidos contado los registros coincidentes
            if self.env['res.partner'].search_count([('name', '=', record5[0])]) >= 1:
                    print('Este contacto ya existe')
                    print(self.env['res.partner'].search_count([('name', '=', record5[0])]))
                # valida y si no hay registros coincidentes almacena un nuevo registro
            if self.env['res.partner'].search_count([('name', '=', record5[0])]) == 0:
                    rec4 = self.env['res.partner'].create(response4)
                    self.env.cr.commit()
                    print(response4)
        #query para filtrar por rango los lotes
        cortes_object = session.query(CortesData).filter(CortesData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()
        #este arreglo recorre el query
        for record in cortes_object:
            global recordObject

            if self.env['cortes'].search_count([('name', '=', record.id_lote_recepcion)]) >= 1:
             print('Folio de corte repetido')
            if self.env['cortes'].search_count([('name', '=', record.id_lote_recepcion)]) == 0:
            #este arreglo busca coincidencias con el nombre del productor en odoo y lo relaciona si ya esta dado de alta
             for line in contactos_obj.search([('name', '=', record.empresa_corte)]):
                line.id
                # este arreglo busca coincidencias con el nombre del productor en odoo y lo relaciona si ya esta dado de alta
             for line2 in huertas_obj.search([('sader', '=', record.sader)]):
                 line2.id
             for line3 in productor_obj.search([('id_productor', '=', record.id_productor)]):
                 line3.id
             for line4 in jefe_acopio_obj.search([('id_jefe_cuadrilla', '=', record.id_jefe_cuadrilla)]):
                 line4.id

             promedio_cajas_corte=0
             if record.peso_productor != 0:
                 promedio_cajas_corte= record.peso_productor / record.cajas_entregadas
             cajas_totales = record.cajas_entregadas_mixto
             if record.cajas_entregadas_mixto == 0:
                 cajas_totales = record.cajas_entregadas

             recordObject = {'name': record.id_lote_recepcion,
                            'id_acuerdo': record.id_acuerdo,
                            'id_orden_corte': record.id_orden_corte,
                            'nombre_productor': line3.id,
                            'huerta': record.huerta,
                            'sader': line2.id,
                            'fecha': record.fecha,
                            'poblacion': record.poblacion,
                            'tipo_corte': record.tipo_corte,
                            'transportista': record.transportista,
                            'empresa_corte': line.id,
                            'jefe_acopio': line4.id,
                            'candado':record.candado,
                            'cajas_entregadas': cajas_totales,
                            'peso_neto': record.peso_neto,
                            'peso_productor': record.peso_productor,
                            'peso_promedio_cajas_corte': promedio_cajas_corte,
                            'bico': record.bico,
                            'ticket': record.ticket,
                            'id_lote':record.id_lote,
                            'tipo_corte_2':record.tipo_corte_2,
                            'peso_nuevo_productor':record.peso_nuevo_productor}
             insert_cortes = self.env['cortes'].create(recordObject)
             self.env.cr.commit()
             print(recordObject)
             #obtiene el id externo del gasto de cuadrilla normal
             id = self.env['tipo_cuadrillas'].search([('name', '=', 'CUADRILLA NORMAL')], limit=1)
             #calculador de tarifa de cuadrilla
             tarifa = 0
             if record.peso_nuevo_productor > 6000:
                 tarifa = record.peso_productor * 1.65
             if record.peso_nuevo_productor < 6000:
                 tarifa = 7500


             # objeto de datos obtenidos name = cuadrillas normal, cudrilla rel = el id que arrojara el almacenamiento
             # del objeto anterior de los cortes, importe = calculo de cuadrilla por Kilogramos
             recordObjectCuadrillasPorCorte = {'name':id.id,
                                               'cuadrilla_rel':insert_cortes.id,
                                               'importe':tarifa}
             insert_cuadrilla_normal = self.env['cuadrillas'].create(recordObjectCuadrillasPorCorte)
             self.env.cr.commit()

        session.close()
        engine.dispose()