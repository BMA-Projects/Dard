# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    prod_seque_id = fields.Many2one('product.sequence', string='Product Sequence')
    prod_categ_id = fields.Many2one('product.category', string='Internal Category')
    
    @api.multi
    @api.onchange('prod_seque_id','prod_categ_id')
    def onchange_prod_id(self):
        if self.prod_categ_id.id and not self.prod_seque_id.id:
            return {'domain':{'product_id':[('sale_ok','=',True),('categ_id','=',self.prod_categ_id.id)]}}
        if not self.prod_categ_id.id and self.prod_seque_id.id:
            return {'domain':{'product_id':[('sale_ok','=',True),('prod_sequence_id','=',self.prod_seque_id.id)]}}
        if self.prod_categ_id.id and self.prod_seque_id.id:
            return {'domain':{'product_id':[('sale_ok','=',True),('prod_sequence_id','=',self.prod_seque_id.id),('categ_id','=',self.prod_categ_id.id)]}}
        if not self.prod_categ_id.id and not self.prod_seque_id.id:
            return {'domain':{'product_id':[('sale_ok','=',True)]}}