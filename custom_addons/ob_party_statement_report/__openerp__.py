# -*- coding: utf-8 -*-
{
    'name': 'Party Statement Report',
    'category': 'Sales and Purchase Management',
    'description':"""
    PDF and Excel report for party statements. 
""",
    'author': 'OfficeBrain',
    'version': '1.0',
    'depends': ['account','stock'],
    'data' : [
           'report/party_statement_report_view.xml',
           'report/party_statement_report_template.xml',
           'report/report_menus.xml'
    ],
    'qweb': [],
    'auto_install': False,
    'installable': True,
    'application': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
