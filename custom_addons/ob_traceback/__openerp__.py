# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'Ob Traceback',
    'version': '2.0',
    'category': 'Tool',
    'description': """
       Suppress error in ERP and display custom error dialog and send mail to authorize user in backend with error description.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['base', 'mail'],
    'data': [
        'security/ob_traceback_security.xml',
        'security/ir.model.access.csv',
        'views/ob_traceback.xml',
        'ob_traceback_view.xml'],
    'demo': [],
    'test': [],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
