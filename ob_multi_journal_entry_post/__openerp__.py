{
    'name': 'Multi Journal Entry Post',
    'version': '8.0',
    'author': 'Atul Makwana',
    'description': """
        This Module is For Confirm Multiple Entries...
    """,
    'summary': 'Confirm Multiple Entries at a same time.',
    'category': 'Acoounting',
    'depends': ['account'],
    'data': [
        'views/account_entries_view.xml',
        'wizard/account_entries_wiz_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
