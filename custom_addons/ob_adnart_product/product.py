# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
    
class product_product(models.Model):
    _inherit = "product.product"

    parent_id = fields.Many2one('product.product')
    prod_attac_ids = fields.Many2many('product.product','product_rel_attachment','prod_att_id','att_id',string='Attachments',domain=[('attachment','=',True)])
    prod_packa_ids = fields.Many2many('product.product','product_rel_packages','prod_pack_id','pack_id',string='Packages',domain=[('packaging','=',True)])
    old_item_id = fields.Float(string="Old Item Id")
    parent_item = fields.Boolean('Is Parent')
    packaging = fields.Boolean('Is Packaging')
    attachment = fields.Boolean('Is attachment')
    product_note = fields.Char('Notes')
    product_size = fields.Char('Size')
    
    @api.multi
    def name_get(self):
        if not 'from_att' in self._context:
            return super(product_product,self).name_get()
        else:
            res = []
            if 'parent_prod_att_id' in self._context:
                for prod in self.browse(self._context.get('parent_prod_att_id')):
                    for prod_id in prod.prod_attac_ids:
                        if prod_id:
                            res.append((prod_id.id,prod_id.name))
            if 'parent_prod_pack_id' in self._context:
                for prod in self.browse(self._context.get('parent_prod_pack_id')):
                    for prod_id in prod.prod_packa_ids:
                        if prod_id:
                            res.append((prod_id.id,prod_id.name))
            return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: