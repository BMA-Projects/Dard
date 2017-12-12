# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _

class product_sequence(models.Model):
    _name = 'product.sequence'

    name = fields.Char('Product Sequence', size=32)
  
class product_template(models.Model):
    _inherit = "product.template"
 
    prod_sequence_id = fields.Many2one('product.sequence', string="Product Sequence",)
    product_group = fields.Char('Product Group', size=32)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: