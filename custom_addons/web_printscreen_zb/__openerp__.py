# -*- encoding: utf-8 -*-

{
    'name': 'Web Printscreen ZB',
    'version': '1.5',
    'category': 'Web',
    'description': """
        Module to export current active tree view in to excel reports
    """,
    'author': 'OfficeBeacon',
    'website': 'bma.officebrain.com',
    'depends': ['web'],
    'data':['views/web_printscreen_export.xml'],
    'qweb': ['static/src/xml/web_printscreen_export.xml'],
    'installable': True,
    'auto_install': False,
    'web_preload': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: