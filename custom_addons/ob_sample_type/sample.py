# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################

from openerp import models, api, fields

class sample_type(models.Model):
    _name = 'sample.type'

    name = fields.Char(string='Sample', size=64)
    description = fields.Char(string='Description', size=128)
    active = fields.Boolean(string='Active')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: