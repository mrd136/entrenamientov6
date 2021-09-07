# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    type_of_document = fields.Selection([
        ('CQ', _('Cheque')),
        ('DP', _('Deposito')),
        ('FCA', _('Factura Anulada')),
        ('EF', _('Efectivo')),
        ('CEI', _('Exencion de IVA')),
        ('FE', _('Factura Especial')),
        ('RA', _('Recibo de Anticipos')),
        ('RC', _('Recibo de Caja')),
        ('RD', _('Recibo Donación')),
        ('CRI', _('Retencion de IVA')),
        ('S1911', _('Constancia de Retención del ISR SAT-1911')),
        ('TF', _('Transferencia')),
        ('RCC', _('Recibo Corriente de Caja')),
        ('OT', _('Otros Documentos'))
    ],
        string="Tipo de Documento", required=True)
    number_of_document = fields.Char(string="Numero de Documento", required=True)
    type_doc_reference = fields.Selection([
        ('CQ', _('Cheque')),
        ('DP', _('Deposito')),
        ('FCA', _('Factura Anulada')),
        ('EF', _('Efectivo')),
        ('CEI', _('Exencion de IVA')),
        ('FE', _('Factura Especial')),
        ('RA', _('Recibo de Anticipos')),
        ('RC', _('Recibo de Caja')),
        ('RD', _('Recibo Donación')),
        ('CRI', _('Retencion de IVA')),
        ('S1911', _('Constancia de Retención del ISR SAT-1911')),
        ('TF', _('Transferencia')),
        ('RCC', _('Recibo Corriente de Caja')),
        ('OT', _('Otros Documentos'))
    ],
        string="Tipo Doc. Referencia", required=True)
    number_doc_reference = fields.Char(string="Numero Doc. Referencia", required=True)
