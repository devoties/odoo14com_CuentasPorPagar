# -*- coding:utf8 -*-

{
    'name': 'Cuentas por pagar Module',
    'version' : '1.0',
    'depends': [
        'base',
        'account',
        'mail',
        'portal',
        'product',
        'purchase',
    ],
    'author': 'ISC Alexis Cruz A',
    'category': 'Cuentas Por Pagar (Interfaz Contpaqi, TTs)',
    'website': 'https://www.bmavocados.com',
    'summary': 'Cuentas Por Pagar Mod',
    'description':'Cuentas Por Pagar Module',
    'data':[
        'security/contratos_security.xml',
        'security/ir.model.access.csv',
        'views/ine_view.xml',
        'views/cif_view.xml',
        'views/menu.xml',
        'views/ciudad_view.xml',
        'views/estado_view.xml',
        'views/pais_view.xml',
        'views/localidad_view.xml',
        'views/huertas_view.xml',
        'views/tipo_contrato_view.xml',
        'views/contratos_compra_venta_view.xml',
        'views/pagos_layout_view.xml',
        'views/account_payment_extends_view.xml',
        'views/facturas_cfdi_3_3_view.xml',
        'data/categoria.xml',
        'data/tipo_cuadrillas.xml',
        'data/organismos_verificadores.xml',
        'data/productos.xml',
        'data/secuencia.xml',
        'data/currency.xml',
        'report/reporte_presupuesto.xml',
        'wizards/lotes_wizard.xml',
        'wizards/cortes_wizard.xml',
        'wizards/cfdis_wizard.xml',
        'views/extension_cuentas_bancarias_view.xml',
        'views/extension_partner_sat_view.xml',
        'views/interfaz_lotes_view.xml',
        'views/interfaz_cortes_view.xml',
        'views/cp_cuadrillas_view.xml',
        'views/registros_certificaciones_view.xml',
        'views/opinion_cumplimiento_view.xml',
        'views/sat_documentos_lotes_view.xml',
        'views/huertas_contratos_view.xml',
        'views/lotes_account_move_line_view.xml',
        'wizards/corte_cuadrillas_ajuste_view.xml',
        #'views/product_product_extends.xml',
        'views/product_product_sat_catalogue_view.xml',
        'views/purchase_order_extends_view.xml',
        'views/pagos_doctos_rel_view.xml',
        'views/presupuesto_lotes_view.xml',
        'views/reporte_saldos.xml',
        'report/reporte_saldos_pendientes.xml',
        'report/reporte_lotes_view.xml',
        'report/reporte_lotes_view2.xml',
        'report/reporte_saldos_facturado_no_pagado.xml',
        'wizards/reportes_saldos_wizard_view.xml'

    ],
}