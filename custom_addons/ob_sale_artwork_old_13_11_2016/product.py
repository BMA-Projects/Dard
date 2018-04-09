# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBrain Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebrain.com)
#
##############################################################################

from openerp.osv import osv, fields
import re

class product_product(osv.osv):
    
    _inherit = 'product.product'
   
    def create(self,cr,uid,vals,context=None):     
        if context is None:
            context = {}
        if vals.get('default_code',False) and not context.get('active_id',False) and vals.get('name',False):
            product_name = re.compile("[a-z,A-Z,-]*[0-9]*").findall(vals['default_code'])[0]            
            context['product_template_name'] = "["+product_name+"] " + vals['name']            
        return super(product_product, self).create(cr, uid, vals, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        name_values =  super(product_product, self).name_get(cr, uid, ids, context=context)
        for product in name_values:
            product_name = product[1]
            product_browse_obj = self.browse(cr,uid,product[0],context=context)
            if product_browse_obj.default_code:
                product_ir = "["+re.compile("[a-z,A-Z,-]*[0-9]*").findall(product_browse_obj.default_code)[0]+"] "
                product_name = product[1].replace(product_ir,'')
            res.append([product[0],product_name])
        return res
   
class product_template(osv.osv):
    
    _inherit = 'product.template'
    
    def create(self,cr,uid,vals,context=None):
        if context is None:
            context = {}
            
        if vals.get('default_code',False):
            product_name = re.compile("[a-z,A-Z,-]*[0-9]*").findall(vals['default_code'])[0]
            vals['name'] = "["+product_name+"] " + vals['name']
            
        if context.get('product_template_name'):            
            vals['name'] = context['product_template_name']
             
        return super(product_template, self).create(cr, uid, vals, context=context)
    

    
    
