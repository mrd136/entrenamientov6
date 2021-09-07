{
    'name': 'Stock ledger report',
    'version': '1.0.101',
    'category': 'Sales',
    'sequence': 1,
    'depends': ['base', 'stock', 'account_reports'],
    'description': """
Stock ledger report
    """,
    'data': [
        # report
        'reports/stock_ledger.xml',

        # views
        'views/assets.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
