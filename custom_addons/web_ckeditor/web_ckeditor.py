# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp.osv import fields, osv, orm

class email_template(osv.osv):
    _inherit = 'email.template'
    
    _columns = {
        'body_html': fields.html('HTML Body')
    }