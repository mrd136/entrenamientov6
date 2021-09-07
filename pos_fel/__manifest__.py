
# -*- coding: utf-8 -*-

{
    'name': 'Point of Sale unido a facturacion electrónica',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Point of Sale unido a facturacion electrónica',
    'description': """ Cambios al Punto de Venta para generar facturas electrónicas fácilmente """,
    'website': 'http://aquih.com',
    'author': 'Rodrigo Fernandez',
    'depends': ['point_of_sale', 'fel_gt'],
    'data': [
        'views/report.xml',
        'views/pos_order_ticket.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos_fel.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
