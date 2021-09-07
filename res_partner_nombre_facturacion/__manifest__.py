# -*- encoding: utf-8 -*-

{
    'name': 'Guatemala - Retorna Datos Cliente',
    'author': 'Piensom',
    'version': '14.0',
    'description': """ Metodo Retorna Datos Cliente para obtener Nombre y Dirección a partir del NIT. """,
    'website': 'http://piensom.com/',
    'depends': ['l10n_gt_extra','fel_gt','fel_megaprint',],
    'data': [
        'views/res_partner_nombre_facturacion.xml',
    ],
    'demo': [],
    'installable': True,
}
