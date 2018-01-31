# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api

class ResPartner(models.Model):
    
    _inherit = "res.partner"

    sales_goal = fields.Float("Sales Goal")
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


 