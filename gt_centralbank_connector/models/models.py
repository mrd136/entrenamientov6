# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import xmltodict
from datetime import datetime, timedelta
import pytz
import requests, json
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError



class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def scheduler_get_usd_rate(self):
        res_currency_usd = self.env.ref('base.USD')
        usd_active = False
        if res_currency_usd.active:
            usd_active= True
        if usd_active:

            url = "https://www.banguat.gob.gt/variables/ws/TipoCambio.asmx"
            xml_body = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
                            <Body>
                                <TipoCambioDia xmlns="http://www.banguat.gob.gt/variables/ws/"/>
                            </Body>
                        </Envelope>"""

            encoded_request = xml_body.encode('utf-8')
            headers = {"Content-Type": "text/xml"}
            response = requests.post(url=url, headers=headers, data=encoded_request)
            response_xml = response.content.decode('utf-8')
            res_dict = xmltodict.parse(response_xml)

            fecha_date = False
            fecha_date_obj = False
            referencia = False

            if res_dict.get('soap:Envelope') and res_dict.get('soap:Envelope').get('soap:Body') and res_dict.get('soap:Envelope').get('soap:Body').get('TipoCambioDiaResponse') and res_dict.get('soap:Envelope').get('soap:Body').get('TipoCambioDiaResponse').get('TipoCambioDiaResult') and res_dict.get('soap:Envelope').get('soap:Body').get('TipoCambioDiaResponse').get('TipoCambioDiaResult').get('CambioDolar') and res_dict.get('soap:Envelope').get('soap:Body').get('TipoCambioDiaResponse').get('TipoCambioDiaResult').get('CambioDolar').get('VarDolar'):
                if res_dict.get('soap:Envelope').get('soap:Body').get('TipoCambioDiaResponse').get('TipoCambioDiaResult').get('CambioDolar').get('VarDolar').get('fecha'):
                    fecha_date = res_dict['soap:Envelope']['soap:Body']['TipoCambioDiaResponse']['TipoCambioDiaResult']['CambioDolar']['VarDolar']['fecha']
                    fecha_date_obj = datetime.strptime(fecha_date, "%d/%m/%Y")
                if res_dict.get('soap:Envelope').get('soap:Body').get('TipoCambioDiaResponse').get('TipoCambioDiaResult').get('CambioDolar').get('VarDolar').get('referencia'):
                    referencia = float(res_dict['soap:Envelope']['soap:Body']['TipoCambioDiaResponse']['TipoCambioDiaResult']['CambioDolar']['VarDolar']['referencia'])

            if fecha_date_obj and referencia:
                company_ids = self.env['res.company'].search([])
                for company in company_ids:
                    if self.env['res.currency.rate'].search([('name', '=', fecha_date_obj.date()), ('company_id', '=', company.id), ('currency_id', '=', res_currency_usd.id) ]):
                        self.env['res.currency.rate'].search([('name', '=', fecha_date_obj.date()), ('company_id', '=', company.id), ('currency_id', '=', res_currency_usd.id)]).rate = 1/referencia

                    else:
                        new_rates = {
                            'company_id': company.id,
                            'currency_id': res_currency_usd.id,
                            'rate' : 1/referencia,
                            'name' : fecha_date_obj.date()
                        }
                        res = self.env['res.currency.rate'].create(new_rates)
        return True


                
