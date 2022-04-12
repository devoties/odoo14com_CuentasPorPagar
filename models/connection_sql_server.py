# -*- coding:utf-8 -*-
import pendulum

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
_logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

Base = declarative_base()


class LotesData(Base):
    __tablename__ = 'Cuentas_Por_Pagar_Productores_Odoo'
    id_movimiento = Column('IdCreditoMovimiento', Integer(), primary_key=True)
    clave = Column('Clave', String(100))
    id_lote = Column('IdLote', Integer())
    nombre_proveedor = Column('Nombre', String(200))
    huerta = Column('huerta',String(200))
    sader = Column('sader',String(200))
    fecha = Column('FechaRecepcion', Date)
    tipo_movimiento = Column('CreditoTipoMovimiento', String(100))
    precio_u = Column('PrecioU',Float)
    importe = Column('Importe', Float)
    cantidad = Column('Kilogramos', Float)
    poblacion = Column('Poblacion',String(200))
    jefe_acopio = Column('JefeAcopio',String(200))
    cajas = Column('Cajas',Integer())
    tipo_corte = Column('TipoCorte',String(200))
    fecha_empacado = Column('FechaEmpacado',Date)
    tickets = Column('Tickets',String(200))
    referencia = Column('Referencia',String(200))
    observaciones = Column('Observaciones', String(200))
    id_productor = Column('IdProductor', Integer())


class LotesDataProductores(Base):
  #  __table_args__ = {'extend_existing': True}
    __tablename__ = 'CuentasPorPagarProductoresCatalogoOdoo'
    id_lote = Column('IdLote',Integer(), primary_key=True)
    nombre = Column('Nombre', String(200))
    id_productor =Column('IdProductor', Integer())
    fecha = Column('FechaRecepcion', Date)

class LotesDataHuertas(Base):
  #  __table_args__ = {'extend_existing': True}
    __tablename__ = 'CuentasPorPagarHuertasCatalogoOdoo'
    id_lote = Column('IdLote',Integer(), primary_key=True)
    sader = Column('sader', String(200))
    huerta = Column('Huerta',String(500))
    nombre_productor = Column('Nombre',String(500))
    id_productor =Column('IdProductor', Integer())
    fecha = Column('FechaRecepcion', Date)

class LotesDataJefeAcopio(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'CuentasPorPagarProductoresCatalogoOdoo'
    id_lote = Column('IdLote',Integer(), primary_key=True)
    nombre = Column('JefeAcopio', String(200))
    id_productor =Column('IdProductor', Integer())
    fecha = Column('FechaRecepcion', Date)

class RecepcionesPorLote(Base):
    __tablename__ = 'View_RecepcionesLotes_ODOO14'
    id_recepcion = Column('IdLoteRecepcion',Integer(),primary_key=True)
    id_lote = Column('NumeroLote',Integer())
    id_orden_corte = Column('OrdenCorte',String(500))
    fecha = Column('FechaR',Date)
    ticket = Column('Ticket',String(500))
    peso_bruto = Column('PesoBruto',Float)
    peso_tara = Column('PesoTara',Float)
    peso_neto = Column('PesoNeto',Float)
    peso_bascula_productor = Column('PesoBasculaProductor',Float)


class Session():
    def session(engine):
        Session = sessionmaker(bind=engine)
        # session = Session()
        session = scoped_session(Session)

        return session

    def engine():
        #server_addres = 'e3210dfde5c7.sn.mynetname.net' + ":" + "49703"
        server_addres = 'e3210dfde5c7.sn.mynetname.net' + ":" + "49703"
        database = 'DLC'
        username = 'sa'
        password = 'HideMyPassBm123*'

        arguments = dict(server=server_addres, user=username,
                         password=password, database=database, charset="utf8")

        engine = sa.create_engine('mssql+pymssql:///', connect_args=arguments)
        return engine

    # Modelo de odoo


class Lotes(models.Model):
    _name = "lotes"
    _inherit=['mail.thread','mail.activity.mixin','portal.mixin']
    _description='Lotes Module'
    # reestriccion por db para id del lote type_unique=(name)
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Datos duplicados en el rango solicitado, revisa tu rango')]

  #    @api.constrains('name')
  #   def _name_valid(self):

  #          raise exceptions.ValidationError("Datos duplicados en el rango solicitado, revisa tu rango")

    name = fields.Integer(string='Numero de lote')

    clave = fields.Char(string='Clave')

    id_credito_mov = fields.Integer(string='IdCreditoMovimiento')

    nombre_proveedor = fields.Char(string='Nombre')

    id_partner = fields.Many2one(string='Nombre', comodel_name='res.partner')

    huerta = fields.Char(string='Huerta')

    sader = fields.Many2one(String='Sader',comodel_name='huertas')

    fecha = fields.Date(string='Fecha')

    tipo_movimiento = fields.Char(string='Tipo de movimiento')

    abono = fields.Float(string='Abono',stored=True)

    saldo_pendiente = fields.Float(string='Saldo pendiente')

    kilogramos_pendientes = fields.Float(string='Kg Pendientes',auto_join=True)

    importe = fields.Float(string='Importe',digits='Product Price')

    precio_u = fields.Float(string='Precio Unitario')

    cantidad = fields.Float(string='Kilogramos')

    observaciones = fields.Char(string='Observaciones')

    poblacion = fields.Char(string='Población')

    jefe_acopio = fields.Many2one(string='Jefe Acopio',comodel_name='res.partner')

    cajas = fields.Char(string='Cajas')

    tipo_corte = fields.Char(String='Tipo de corte')

    fecha_empacado = fields.Date(string='Fecha Empacado')

    tickets = fields.Char(string='Tickets')

    referencia = fields.Char(string='Referencia')

    active = fields.Boolean(string='Activo', default=True)

    es_doc_bico = fields.Boolean(string='¿Bico?',default=True)

    doc_bico = fields.One2many('sat_documentos_lotes','bico_lotes_rel',string='Bico')

    adicionales = fields.Char(string='Adicionales',tracking=True,track_visibility='always') #onchange

    #cfdis_relacionados = fields.Many2many('account.move','lotes_cfdi','lotes_id','account_move_id',tracking=True,track_visibility='onchange',string='Cfdis Relacionados')

    status_facturas = fields.Char(string='Estatus Factura',store=True)

    status_pago = fields.Char(string='Estatus Pago')

    status_provision = fields.Char(string='Provision Lotes',compute='compute_abonos',
                                   copy=False,tracking=True,track_visibility='always',readonly=True,stored=True)

    seats = fields.Integer(string='Numeber of seats')

    id_productor = fields.Integer(string='Id Productor In')

    kilogramos_abonados_v = fields.Float(string='Kg abonados')

    kilogramos_pendientes_v = fields.Float(string='Kg Pendientes',compute='compute_abonos',stored=True)

    fecha_contabilizacion = fields.Datetime(string='Fecha Aprobado', copy=False,tracking=True,track_visibility='always')

    lotes_detalle = fields.One2many('lotes_account_move_line','name',string='Lotes Detalle')

    no_movimientos = fields.One2many('lotes_account_move_line', 'name', string='No. Movimientos')


    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('Contabilizado Lote', 'Contabilizado Lote'),
        ('Contabilizado Cfdi', 'Contabilizado Cfdi'),

    ], default='borrador', string='Estados', copy=False,tracking=True,track_visibility='always',readonly=True,stored=True)

    estado_pago = fields.Selection(related='lotes_detalle.estado_factura',string='Estado Pago')

    uuid = fields.Char(related='lotes_detalle.uuid')

    serie = fields.Char(related='lotes_detalle.serie')

    folio = fields.Char(related='lotes_detalle.folio')

    estado_factura = fields.Selection(string='Estado Factura',related='lotes_detalle.estado_pago')

    uuid_search = fields.Char(string='Uuid',compute='listar_datos_cfdi')

    serie_search = fields.Char(string='Serie', compute='listar_datos_cfdi')

    folio_search = fields.Char(string='Folio', compute='listar_datos_cfdi')

    emisor_search = fields.Char(string='Emisor', compute='listar_datos_cfdi')

    fecha_factura_search = fields.Char(string='Fecha Factura',compute='listar_datos_cfdi')

    @api.depends('uuid_search','serie_search','folio_search','emisor_search')
    def listar_datos_cfdi(self):
        for line in self:
            uuid_res = line.env['lotes_account_move_line'].search([('name.name', '=', line.name)]).mapped('uuid')
            serie_res = line.env['lotes_account_move_line'].search([('name.name', '=', line.name)]).mapped('serie')
            folio_res = line.env['lotes_account_move_line'].search([('name.name', '=', line.name)]).mapped('folio')
            emisor_res = line.env['lotes_account_move_line'].search([('name.name', '=', line.name)]).mapped('id_partner.name')
            fecha_factura_res = line.env['lotes_account_move_line'].search([('name.name', '=', line.name)]).mapped('fecha_factura')
            line.uuid_search = uuid_res
            line.serie_search = serie_res
            line.folio_search = folio_res
            line.emisor_search = emisor_res
            line.fecha_factura_search = fecha_factura_res


    def compute_abonos(self):
        for lote in self:
            records_sum = sum(lote.env["lotes_account_move_line"].search([('name.name', '=', lote.name)]).mapped('abono_kilogramos'))
            lote.kilogramos_abonados_v = records_sum
            if lote.cantidad == records_sum:
                lote.status_provision = 'Provisionado Totalmente'
            if lote.cantidad > records_sum and records_sum > 0:
                lote.status_provision = 'Provisinado Parcialmente'
            if records_sum == 0:
                lote.status_provision = 'No Provisionado'
            lote.kilogramos_abonados_v = records_sum
            lote.kilogramos_pendientes_v = lote.cantidad - records_sum
            lote.abono = records_sum


    def contabilizar_lote(self):
        for line in self:
         line.state = 'Contabilizado Lote'
         line.fecha_contabilizacion = fields.Datetime.now()

    def contabilizar_cfdi(self):
        for line in self:
         line.state = 'Contabilizado Cfdi'
         line.fecha_contabilizacion = fields.Datetime.now()


    def convertir_a_borrador(self):
        for line in self:
         line.state = 'borrador'



    @api.depends('cfdis_relacionados')
    def get_importe_factura(self):
        global total
        rec_facturas = 0
        for rec_facturas in self:
            total = 0.0
        for line in rec_facturas.cfdis_relacionados:
         total += line.amount_total
        if self.importe == total:
            self.status_facturas = 'Completo'
        if self.importe != total:
            self.status_facturas = 'Incompleto'


    @api.onchange('cfdis_relacionados')
    def _onchange_cfdis(self):

     if len(self.cfdis_relacionados) == 0:
        print(0)
     if len(self.cfdis_relacionados) > 0:
        return self.get_importe_factura()

    def _onchange_cfdis2(self):

     if len(self.cfdis_relacionados) == 0:
        return self.get_importe_factura()
     if len(self.cfdis_relacionados) > 0:
        return self.get_importe_factura()

#Descarga datos TTS
    def download_data(self):
        engine = Session.engine()
        session = Session.session(engine)

        # valores globales para llamar el objeto fuera del modelo
        global lotes_object
        # ordenar por nombre
        # lote_inicial_object.search([],order='name')
        rango_lotes_obj = self.env['lotes_wizard']
        contactos_obj = self.env['res.partner']
        huertas_obj = self.env['huertas']
        recepciones_lotes_obj = self.env['recepciones_lotes']

        for i in rango_lotes_obj.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.fecha_inicial
            i.fecha_final
        #Query que genera unico el catalogo de productores dependiendo del rango de lotes
        lotes_object_cat_productores = session.query(distinct(LotesDataProductores.id_productor),LotesDataProductores.nombre)\
            .filter(LotesDataProductores.fecha.between(i.fecha_inicial, i.fecha_final)).all()
        lotes_object_cat_huertas = session.query(distinct(LotesDataHuertas.sader),LotesDataHuertas.huerta,LotesDataHuertas.id_productor)\
            .filter(LotesDataHuertas.fecha.between(i.fecha_inicial, i.fecha_final)).all()
        lotes_object_cat_jefe_acopio = session.query(distinct(LotesDataJefeAcopio.nombre),LotesDataJefeAcopio.nombre)\
            .filter(LotesDataJefeAcopio.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()

        #print(recepciones_lotes_object_data)


        #arreglo que recorre el objeto
        for record2 in lotes_object_cat_productores:
            #variable global para respuesta del query
            global response
            response = ''
            #agregar datos de al diccionario python
            id_category_productor = self.env.ref('cuentas_por_pagar.category_productor')
            response = {'id_productor': record2[0],
                        'name': record2[1],
                        'category_id': id_category_productor}
            #valida que no halla registros repetidos contado los registros coincidentes
            if self.env['res.partner'].search_count([('id_productor', '=', record2[0])]) >= 1:
                print('Este contacto ya existe')
                print(self.env['res.partner'].search_count([('id_productor', '=', record2[0])]))
            #valida y si no hay registros coincidentes almacena un nuevo registro
            if self.env['res.partner'].search_count([('id_productor', '=', record2[0])]) == 0:
                rec = self.env['res.partner'].create(response)
                self.env.cr.commit()
                print(response)

                # arreglo que recorre el objeto
        for record3 in lotes_object_cat_huertas:
                # variable global para respuesta del query
            global response2
            response2 = ''
            for row in contactos_obj.search([('id_productor', '=', record3.id_productor)]):
                row.id

                # agregar datos de al diccionario python
            response2 = {'name': record3[1],
                         'sader': record3[0],
                          'productor':row.id}
                # valida que no halla registros repetidos contado los registros coincidentes
            if self.env['huertas'].search_count([('sader', '=', record3[0])]) >= 1:
                print('Este huerto ya existe')
                print(self.env['huertas'].search_count([('sader', '=', record3[0])]))
                # valida y si no hay registros coincidentes almacena un nuevo registro
            if self.env['huertas'].search_count([('sader', '=', record3[0])]) == 0:
                rec2 = self.env['huertas'].create(response2)
                self.env.cr.commit()
                print(response2)

        for record4 in lotes_object_cat_jefe_acopio:
                # variable global para respuesta del query
            global response3
            response3 = ''
                # agregar datos de al diccionario python
            response3 = {'name': record4[0]}
                # valida que no halla registros repetidos contado los registros coincidentes
            if self.env['res.partner'].search_count([('name', '=', record4[0])]) >= 1:
                print('Este huerto ya existe')
                print(self.env['res.partner'].search_count([('name', '=', record4[0])]))
                # valida y si no hay registros coincidentes almacena un nuevo registro
            if self.env['res.partner'].search_count([('name', '=', record4[0])]) == 0:
                rec3 = self.env['res.partner'].create(response3)
                self.env.cr.commit()
                print(response3)

        #query para filtrar por rango los lotes
        lotes_object = session.query(LotesData).filter(LotesData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()
        #este arreglo recorre el query
        for record in lotes_object:
            global recordObject
            if self.env['lotes'].search_count([('name', '=', record.id_lote)]) >= 1:
             print('Folio de lote repetido')
            if self.env['lotes'].search_count([('name', '=', record.id_lote)]) == 0:
            #este arreglo busca coincidencias con el nombre del productor en odoo y lo relaciona si ya esta dado de alta
             for line in contactos_obj.search([('id_productor', '=', record.id_productor)]):
                line.id
            # este arreglo busca coincidencias con el nombre del productor en odoo y lo relaciona si ya esta dado de alta
             for line2 in huertas_obj.search([('sader', '=', record.sader)]):
                line2.id
             for line3 in contactos_obj.search([('name', '=', record.jefe_acopio)]):
                line3.id
             #Inserta las recepciones de cada linea del lote
             recepciones_lotes_object_data = session.query(RecepcionesPorLote).filter(
                RecepcionesPorLote.fecha.between(i.fecha_inicial, i.fecha_final)).filter(RecepcionesPorLote.id_lote == record.id_lote)\
                 .all()
             for line_recepciones in recepciones_lotes_object_data:
                 global recordRecepcionesObject

                 recordRecepcionesObject = {'name':line_recepciones.id_recepcion,
                                            'id_lote':line_recepciones.id_lote,
                                            'id_orden_corte':line_recepciones.id_orden_corte,
                                            'fecha':line_recepciones.fecha,
                                            'ticket':line_recepciones.ticket,
                                            'peso_bruto':line_recepciones.peso_bruto,
                                            'peso_tara':line_recepciones.peso_tara,
                                            'peso_neto':line_recepciones.peso_neto,
                                            'peso_bascula_productor':line_recepciones.peso_bascula_productor}

                 print(recordRecepcionesObject)

                 #insert = self.env['recepciones_lotes'].create(recordRecepcionesObject)
                 #self.env.cr.commit()

             recordObject = {'name': record.id_lote,
                            'id_credito_mov': record.id_movimiento,
                            'clave': record.clave,
                            'id_partner': line.id,
                           # 'huerta': record.huerta,
                            'sader': line2.id,
                            'fecha': record.fecha,
                            'tipo_movimiento': record.tipo_movimiento,
                            'importe': record.precio_u*record.cantidad,
                            'precio_u': record.precio_u,
                            'cantidad': record.cantidad,
                            'observaciones': record.observaciones,
                            'poblacion':record.poblacion,
                            'jefe_acopio':line3.id,
                            'cajas':record.cajas,
                            'tipo_corte': record.tipo_corte,
                            'fecha_empacado': record.fecha_empacado,
                            'tickets': record.tickets,
                            'referencia': record.referencia,
                            'saldo_pendiente':record.cantidad*record.precio_u,
                            'kilogramos_pendientes':record.cantidad}
             insert = self.env['lotes'].create(recordObject)
             self.env.cr.commit()
             print(recordObject)

        session.close()
        engine.dispose()





