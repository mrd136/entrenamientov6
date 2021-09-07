{
    'name': 'Town Address',
    'version': '13.0.0.0.1',
    'category': 'Sale',
    'summary': 'Town Address',
    'description': """Town Address""",
    'depends': ['base', 'contacts', 'sale_management'],
    "data": [
        'security/ir.model.access.csv',
        'data/res.town.csv',
        'views/res_town_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
