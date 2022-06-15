# -*- coding:utf-8 -*-
import requests

from odoo import fields, models, api, _
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, Session
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import Integer, String, Float, SmallInteger, Numeric, DateTime, Date
from sqlalchemy import distinct
import logging

_logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

Base = declarative_base()


# Clase de movimientos de recepcion
class CortesData(Base):
    __tablename__ = 'ZZZ_RecepcionLotes'
    id_acuerdo = Column('IdAcuerdo', Integer())
    id_orden_corte = Column('IdOrdenCorte', Integer())
    id_lote_recepcion = Column('IdLoteRecepcion', Integer(), primary_key=True)
    nombre_productor = Column('Nombre', String(500))
    huerta = Column('Huerta', String(500))
    sader = Column('NoRegistro', String(500))
    fecha = Column('Fecha', DateTime)
    poblacion = Column('Poblacion', String(500))
    tipo_corte = Column('TipoCorte', String(500))
    precio = Column('Precio', Float)
    transportista = Column('Expr2', String(500))
    empresa_corte = Column('Expr3', String(500))
    jefe_acopio = Column('Expr4', String(200))
    candado = Column('Candado', String(200))
    cajas_entregadas = Column('CajasCortadas', Integer())
    peso_neto = Column('PesoNeto', Float)
    peso_productor = Column('PesoBasculaProductor', Float)
    bico = Column('COPREF', String(200))
    ticket = Column('Ticket', String(200))
    id_productor = Column('IdProductor', Integer())
    id_jefe_cuadrilla = Column('IdJefeCuadrilla', Integer())


class Session():
    def session(engine):
        Session = sessionmaker(bind=engine)
        # session = Session()
        session = scoped_session(Session)

        return session

    def engine():
        # server_addres = '192.168.88.214' + ":" + "49703"
        server_addres = 'e3210dfde5c7.sn.mynetname.net' + ":" + "49703"
        database = 'TTS'
        username = 'sa'
        password = 'HideMyPassBm123*'

        arguments = dict(server=server_addres, user=username,
                         password=password, database=database, charset="utf8")

        engine = sa.create_engine('mssql+pymssql:///', connect_args=arguments)
        return engine

    # Modelo de odoo


class Fletes(models.Model):
    _name = "fletes"

    name = fields.Char(string='')

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

        cortes_object = session.query(CortesData).filter(
            CortesData.fecha.cast(Date).between(i.fecha_inicial, i.fecha_final)).all()
        # este arreglo recorre el query
        for record in cortes_object:
            global recordObject

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
                            'candado': record.candado,
                            'cajas_entregadas': record.cajas_entregadas,
                            'peso_neto': record.peso_neto,
                            'peso_productor': record.peso_productor,
                            'bico': record.bico,
                            'ticket': record.ticket, }
            insert_cortes = self.env['cortes'].create(recordObject)
            self.env.cr.commit()
            print(recordObject)
            # obtiene el id externo del gasto de cuadrilla normal
            id = self.env['tipo_cuadrillas'].search([('name', '=', 'CUADRILLA NORMAL')], limit=1)
            # calculador de tarifa de cuadrilla
            tarifa = 0
            if record.peso_productor > 5000:
                tarifa = record.peso_productor * 1.65
            if record.peso_productor < 5000:
                tarifa = 7500

            # objeto de datos obtenidos name = cuadrillas normal, cudrilla rel = el id que arrojara el almacenamiento
            # del objeto anterior de los cortes, importe = calculo de cuadrilla por Kilogramos
            recordObjectCuadrillasPorCorte = {'name': id.id,
                                              'cuadrilla_rel': insert_cortes.id,
                                              'importe': tarifa}
            insert_cuadrilla_normal = self.env['cuadrillas'].create(recordObjectCuadrillasPorCorte)
            self.env.cr.commit()

    session.close()
    engine.disp