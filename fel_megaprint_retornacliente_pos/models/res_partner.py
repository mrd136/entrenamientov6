# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round

import base64
from lxml import etree
import requests

import html
import uuid

import logging


class ResPartner(models.Model):
    _inherit = "res.partner"


    def get_name(self):
        for partner in self:
            request_url = "apiv2"
            request_path = ""
            request_url_firma = ""
            if self.env.company.pruebas_fel:
                request_url = "dev2.api"
                request_path = ""
                request_url_firma = "dev."

            if partner.vat and self.env.company.usuario_fel:
                headers = { "Content-Type": "application/xml" }
                data = '<?xml version="1.0" encoding="UTF-8"?><SolicitaTokenRequest><usuario>{}</usuario><apikey>{}</apikey></SolicitaTokenRequest>'.format(self.env.company.usuario_fel, self.env.company.clave_fel)
                r = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/solicitarToken', data=data.encode('utf-8'), headers=headers)
                resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
                if len(resultadoXML.xpath("//token")) > 0:
                    token = resultadoXML.xpath("//token")[0].text
                else:
                    raise UserError('Credenciales Inválidas')    
                direcciones = []    
                nit = partner.vat.replace("-", "")
                body = '<?xml version="1.0" encoding="UTF-8"?><RetornaDatosClienteRequest><nit>{}</nit></RetornaDatosClienteRequest>'.format(nit)
                headers = { "Content-Type": "application/xml", "authorization": "Bearer "+token }
                r = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/retornarDatosCliente', data=body.encode('utf-8'), headers=headers)
                resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
                
                if len(resultadoXML.xpath("//nombre")) > 0:
                    nombre = resultadoXML.xpath("//nombre")[0].text
                    partner.nombre_facturacion_fel = nombre     
                    if len(resultadoXML.xpath("//direccion")) > 0:
                        for x in range(len(resultadoXML.xpath("//direccion"))):
                            direcciones.append(resultadoXML.xpath("//direccion")[x].text)
                        if not partner.street:    
                            partner.street = direcciones[-1]    
                else:
                    raise UserError('Datos no encontrados. Verifique si el NIT es correcto.')
                   
                #raise UserError(direcciones)    
            return

    def get_name_and_street_from_vat(self,vat=''):
        street=''
        name=''

        request_url = "apiv2"
        request_path = ""
        request_url_firma = ""
        if self.env.company.pruebas_fel:
            request_url = "dev2.api"
            request_path = ""
            request_url_firma = "dev."

        if vat and self.env.company.usuario_fel:
            headers = {"Content-Type": "application/xml"}
            data = '<?xml version="1.0" encoding="UTF-8"?><SolicitaTokenRequest><usuario>{}</usuario><apikey>{}</apikey></SolicitaTokenRequest>'.format(self.env.company.usuario_fel, self.env.company.clave_fel)
            r = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/solicitarToken', data=data.encode('utf-8'), headers=headers)
            resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))
            if len(resultadoXML.xpath("//token")) > 0:
                token = resultadoXML.xpath("//token")[0].text
            else:
                raise UserError('Credenciales Inválidas')
            direcciones = []
            nit = vat.replace("-", "")
            body = '<?xml version="1.0" encoding="UTF-8"?><RetornaDatosClienteRequest><nit>{}</nit></RetornaDatosClienteRequest>'.format(nit)
            headers = {"Content-Type": "application/xml", "authorization": "Bearer " + token}
            r = requests.post('https://'+request_url+'.ifacere-fel.com/'+request_path+'api/retornarDatosCliente', data=body.encode('utf-8'), headers=headers)
            resultadoXML = etree.XML(bytes(r.text, encoding='utf-8'))

            if len(resultadoXML.xpath("//nombre")) > 0:
                name = resultadoXML.xpath("//nombre")[0].text
                if len(resultadoXML.xpath("//direccion")) > 0:
                    for x in range(len(resultadoXML.xpath("//direccion"))):
                        direcciones.append(resultadoXML.xpath("//direccion")[x].text)
                    street = direcciones[-1]
        return {'street':street,'name':name}
        
