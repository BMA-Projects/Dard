# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    'name': 'OB DARD FTP',
    'version': '1.0',
    'author': 'OfficeBrain',
    'summary': """""",
    'description': """This module is to generate csv data file and upload those over ftp """,
    'license': '',
    'website': 'http://www.officebrain.com',
    'images': [],
    'depends': ['base', 'sale','account','stock','ob_sale_artwork'], # ob_sale_artwork required only for field 'client_po_ref'
    'category': 'Tools',
    'data': [
        'views/ftp_config_cron.xml',
        'views/ftp_config_view.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
