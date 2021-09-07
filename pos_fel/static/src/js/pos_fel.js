odoo.define('pos_fel.pos_fel', function (require) {
    "use strict";
    
    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const PosComponent = require('point_of_sale.PosComponent');

    const Registries = require('point_of_sale.Registries');

    const { useState } = owl.hooks;
    
    const PosFELOrderReceipt = (OrderReceipt) =>
        class extends OrderReceipt {
            constructor() {
                super(...arguments);
                var self = this;
                this.state = useState({ fel_gt: { firma_fel: '', serie_fel: '', numero_fel: '', certificador_fel: '' } });
                // var state = this.state;
                
                this.rpc({
                    model: 'pos.order',
                    method: 'search_read',
                    args: [[['pos_reference', '=', this.props.order.name]], ["firma_fel", "serie_fel", "numero_fel", "certificador_fel"]],
                }, {
                    timeout: 5000,
                }).then(function (orders) {
                    console.log(orders);
                    if (orders.length > 0) {
                        
                        self.state.fel_gt.firma_fel = orders[0].firma_fel;
                        self.state.fel_gt.serie_fel = orders[0].serie_fel || 'serie_fel';
                        self.state.fel_gt.numero_fel = orders[0].numero_fel || 'numero_fel';
                        self.state.fel_gt.certificador_fel = orders[0].certificador_fel || 'ecofactura';
                        
                        /*
                        var env = self.get_receipt_render_env();
                        var precio_total_descuento = 0;
                        var precio_total_positivo = 0;
                         
                        env['orderlines'].forEach(function(linea) {
                            if (linea.get_unit_price() > 0) {
                                precio_total_positivo += linea.get_price_with_tax();
                            } else if (linea.get_unit_price() < 0) {
                                precio_total_descuento += linea.get_price_with_tax();
                            }
                        });
                        
                        env['precio_total_descuento'] = precio_total_descuento;
                        
                        var descuento_porcentaje_fel = precio_total_descuento / precio_total_positivo * -1;
                        env['orderlines'].forEach(function(linea) {
                            if (linea.get_unit_price() > 0) {
                                linea.descuento_porcentaje_fel = descuento_porcentaje_fel * 100;
                                linea.descuento_nominal_fel = linea.get_price_with_tax() * descuento_porcentaje_fel;
                            } else if (linea.get_unit_price() < 0) {
                                linea.descuento_porcentaje_fel = 100;
                                linea.descuento_nominal_fel = linea.get_price_with_tax();
                            }
                        });
                        
                        self.$('.pos-receipt-container').html(QWeb.render('OrderReceipt', env));
                        */
                    }
                });
            }
        };
        
    Registries.Component.extend(OrderReceipt, PosFELOrderReceipt);

});
