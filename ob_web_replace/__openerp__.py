# -*- coding: utf-8 -*-
{
    'name': 'Web Replace',
    'category': 'Hidden',
    'description':"""
OpenERP Web view.
==========================

""",
    'author': 'OfficeBrain',
    'version': '2.0',
    'depends': ['base','web','web_kanban','base_import','mail','account'],
    'data' : [
         'views/web_view_replace.xml',
         'ob_web_replace_view.xml',
         'res_company_data.xml',
    ],
    'qweb': ['static/src/xml/web_replace.xml'],
    'auto_install': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
