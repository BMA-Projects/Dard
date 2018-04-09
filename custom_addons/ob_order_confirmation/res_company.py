# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, fields, api, _

class res_company(models.Model):
    _inherit = 'res.company'

    support_email = fields.Char(size=64, string="Support Email")
    support_phone = fields.Char(size=64, string="Support Phone")