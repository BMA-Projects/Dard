# -*- coding: utf-8 -*-

##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

{
    'name': 'OB Field Level Access Rights ',
    'version': '0.1',
    'description': """
This module is used for apply access rights (Read only/Invisible/Editable) on fields from front-end.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'depends': ['base'],
    'data': [
        'views/ir_model_fields_view.xml',
        'views/res_groups_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
