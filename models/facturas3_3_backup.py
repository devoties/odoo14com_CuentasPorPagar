# -*- coding:utf-8 -*-

from odoo import fields, models, api
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
#Clase para descargar encabezados de contpaqi contabilidad
class CfdisContpaqiData(Base):
    #Tabla comprobante contpaqi contiene las cabeceras de todos los CFDI
    __tablename__ = 'dbo.Comprobantes'
    #todos los campos del cfdi 3.3
    uuid = Column('UUID',String(600), primary_key=True)
    #fecha_filtro = Column('Fecha_filtro',Date)
    fecha_mes = Column('FechaMes',String(500))
    fecha_anio = Column('FechaAnio',String(200))
    forma_de_pago = Column('FormaPago', String(500))
    forma_de_pago_desc = Column('FormaPagoDesc',String(500))
    condiciones_de_pago = Column('CondicionesPago',String(500))
    subtotal = Column('Subtotal', Float)
    descuento = Column('Descuento', Float)
    tipo_cambio = Column('TipoCambio', Float)
    moneda = Column('Moneda', String(500))
    moneda_desc = Column('MonedaDesc',String(500))
    total = Column('Total', Float)
    tipo_comprobante = Column('TipoComprobante', String(500))
    metodo_pago = Column('MetodoPago', String(500))
    metodo_pago_desc = Column('MetodoPagoDesc', String(500))
    lugar_exp = Column('LugarExp', String(500))
    lugar_exp_desc = Column('LugarExpDesc', String(500))
    fecha_timbrado = Column('FechaTimbrado', DateTime)
    fecha_timbrado_mes = Column('FechaTimbradoMes', String(500))
    fecha_timbrado_anio = Column('FechaTimbradoAnio', String(500))
    numero_certificado = Column('NumeroCertificado', String(500))
    confirmacion = Column('Confirmacion', String(500))
    tipo_documento = Column('TipoDocumento', String(500))
    residencia_fiscal = Column('ResidenciaFiscal', String(500))
    residencia_fiscal_desc = Column('ResidenciaFiscalDesc', String(500))
    num_registro_id_trib = Column('NumRegIdTrib', String(500))
    uso_cfdi = Column('UsoCFDI', String(500))
    uso_cfdi_desc = Column('UsoCFDI_Desc', String(500))
    tipo_comprobante_desc = Column('TipoComprobanteDesc', String(500))
    num_cuenta = Column('NumCta', String(500))

class Session():
    def session(engine):
        Session = sessionmaker(bind=engine)
            # session = Session()
        session = scoped_session(Session)

        return session

    def engine():
        server_addres = 'b8970b8f20a4.sn.mynetname.net' + ":" + "49706"
        database = 'document_b293efb8-0254-4a13-8ab5-dd78af6bfc8b_metadata'
        username = 'sa'
        password = 'HideMyPassBm123'

        arguments = dict(server=server_addres, user=username,
                             password=password, database=database, charset="utf8")

        engine = sa.create_engine('mssql+pymssql:///', connect_args=arguments)
        return engine

        # Modelo de odoo

class FacturaCfdi(models.Model):
    _inherit = 'account.move'

    lotes_relacion = fields.Many2many(comodel_name='lotes',string='Lotes relación')

    uuid = fields.Char(string='Uuid')

    guid_document = fields.Char(string='Guid Document')

    rfc_emisor = fields.Char(string='RFC Emisor')

    nombre_emisor = fields.Char(string='Nombre Emisor')

    regimen_emisor = fields.Char(string='Regimen Emisor')

    regimen_emisor_desc = fields.Char(string='Regimen Emisor Desc')

    curp_emisor = fields.Char(string='CURP Emisor')

    rfc_receptor = fields.Char(string='RFC Receptor')

    nombre_receptor = fields.Char(string='Regimen Receptor')

    total_impuestos_retenidos = fields.Float(string='Total de impuestos retenidos')

    total_impuestos_traslado = fields.Float(string='Total Impuestos Traslado')

    version = fields.Char(string='Versión')

    serie = fields.Char(string='Serie')

    folio = fields.Char(string='Folio')

    fecha = fields.Datetime(string='Fecha')

    fecha_filtro = fields.Date(string='Fecha filtro')

    fecha_mes = fields.Char(string='Fecha Mes')

    fecha_anio = fields.Char(string='Fecha Año')

    forma_de_pago = fields.Char(string='Forma de pago')

    forma_de_pago_desc = fields.Char(string='Forma de pago desc')

    condiciones_de_pago = fields.Char(string='Condicones de pago')

    subtotal = fields.Float(string='Subtotal')

    descuento = fields.Float(string='Descuento')

    tipo_cambio = fields.Float(string='Tipo de cambio')

    moneda = fields.Char(string='Moneda')

    moneda_desc = fields.Char(string='Moneda Desc')

    total = fields.Float(string='Total')

    tipo_comprobante = fields.Char(string='Tipo de comprobante')

    metodo_pago = fields.Char(string='Metodo de pago')

    metodo_pago_desc = fields.Char(string='Metodo de pago desc')

    lugar_exp = fields.Char(string='Lugar Exp')

    lugar_exp_desc = fields.Char(string='Lugar Exp Desc')

    fecha_timbrado = fields.Datetime(string='Fecha timbrado')

    fecha_timbrado_mes = fields.Char(string='Fecha Timbrado Mes')

    fecha_timbrado_anio = fields.Char(string='Fecha Timbrado Año')

    numero_certificado = fields.Char(string='Número certificado')

    confirmacion = fields.Char(string='Confirmación')

    tipo_documento = fields.Char(string='Tipo Documento')

    residencia_fiscal = fields.Char(string='Residencia Fiscal')

    residencia_fiscal_desc = fields.Char(string='Residencia Fiscal Desc')

    num_registro_id_trib = fields.Char(string='Num registro identificación tributaria')

    uso_cfdi = fields.Char(string='Uso de cfdi')

    uso_cfdi_desc = fields.Char(string='Uso de cfdi desc')

    tipo_comprobante_desc = fields.Char(string='Tipo Comprobante Desc')

    num_cuenta = fields.Char(string='Num cuenta')


    def download_data(self):
        engine = Session.engine()
        session = Session.session(engine)

        global cfdi_contpaqi

        rango_cfdis_obj = self.env['cfdis_wizard']


        for i in rango_cfdis_obj.search([], order='id desc', limit=1):
            # ordenar por nombre
            # lote_inicial_object.search([],order='name')
            i.fecha_inicial
            i.fecha_final

        cfdis_objeto = session.query(CfdisContpaqiData).limit(5)

        for record in cfdis_objeto:
            global recordObject

            if self.env['account.move'].search_count([('uuid', '=', record.uuid)]) >= 1:
             print('Cfdi repetido')
            if self.env['account.move'].search_count([('uuid', '=', record.uuid)]) == 0:

             print('no existen datos repetidos')
             #objecto donde se almacena el diccionario a dar de alta
             recordObject = {'uuid': record.uuid}
             insert = self.env['account.move'].create(recordObject)
             self.env.cr.commit()
             print(recordObject)

        session.close()
        engine.dispose()