# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
{
    "name" : 'Web Ckeditor',
    "version" : "0.1",
    "depends" : [ "web", "email_template" ],
    "author" : "officebeacon",
    'description':
        """
OpenERP Web CkEditor module.
============================
This module provides the CkEditor to mail and upload image on server with OpenERP.
        """,
    "installable" : True,
    "auto_install": False,
    'data': ['views/web_ckeditor.xml'],
    
}
