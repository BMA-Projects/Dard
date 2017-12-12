# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'SO Hide Module Details',
    'version': '2.0',
    'category': 'Other',
    'description': """
       1) Make Invisible fields : author, website and license (Not usable right now)
       2) Added Group to hide Settings > Modules menu on un check Module Features checkbox
       3) Module will be installed on time of database creation.

""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com',
    'images': [],
    'depends': ['base'],
    'data': [
        'security/ob_hide_module_security.xml',
        'security/ir.model.access.csv',
        'ob_hide_module.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
