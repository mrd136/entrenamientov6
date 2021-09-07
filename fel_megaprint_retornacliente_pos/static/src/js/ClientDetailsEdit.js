odoo.define('res_partner_nombre_facturacion.ClientDetailsEdit', function(require) {

    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');
    const Registries = require('point_of_sale.Registries');
    const session = require('web.session');

    const VATClientDetailsEdit = ClientDetailsEdit => class extends ClientDetailsEdit {
        captureChange(event) {
            this.changes[event.target.name] = event.target.value;
            self=this;
            if(event.target.name == 'vat'){
            this.rpc({
                model: 'res.partner',
                method: 'get_name_and_street_from_vat',
                args: [[],event.target.value],
            }).then(function (result) {
            if(result!={}){
                self.props.partner.street = result.street;
                self.props.partner.name = result.name;
                self.changes.street = result.street;
                self.changes.name = result.name;
                self.render();
            }
        });

            }
        }
    };

    Registries.Component.extend(ClientDetailsEdit, VATClientDetailsEdit);

    return ClientDetailsEdit;
});
