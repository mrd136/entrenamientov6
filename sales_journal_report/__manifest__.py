# -*- coding: utf-8 -*-
{
    'name': 'Sales Journal Report',
    'version': '14.0.2.0',
    'author': 'Ketan Kachhela',
    'summary': 'Sales Journal Report',
    'description': """Sales Journal Accounting Report""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sales_journal_report_wizard.xml',
        'report/sales_journal_report.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
}
