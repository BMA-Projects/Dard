# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################


{
    'name': 'OffieBrain Canadian Localization CRM',
    'version': '2.0',
    'category': 'Other',
    'description': """
       1) Replace State label Placeholder to Provinces.
       2) Rename Zip label and Placeholder to PostalCode.
       3) State field display state code rather then state name.
""",
    'author': 'OfficeBrain',
    'website': 'http://www.officebrain.com/',
    'images': [],
    'depends': ['base', 'crm'],
    'data': ['canadian_localization.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
