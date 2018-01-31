# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
###############################################################################

import openerp
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv

class so_hide_modules(osv.osv_memory):
    _inherit = 'ir.module.module'
