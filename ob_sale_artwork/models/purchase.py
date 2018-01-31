# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
import re

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    virtual_file_ids = fields.One2many('virtual.file', 'purchase_line_id', 'Virtual File')
    art_approval_file_ids = fields.One2many('sale.order.line.images','purchase_line_id','Art Approval File')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)

class procurement_order(models.Model):
    _inherit = 'procurement.order'
    
    sub_origin = fields.Char('Sub Source Document', size=32)
    
    @api.v7
    def make_po(self, cr, uid, ids, context=None):
        """ Resolve the purchase from procurement, which may result in a new PO creation, a new PO line creation or a quantity change on existing PO line.
        Note that some operations (as the PO creation) are made as SUPERUSER because the current user may not have rights to do it (mto product launched by a sale for example)

        @return: dictionary giving for each procurement its related resolving PO line.
        """
        po_line_obj = self.pool.get('purchase.order.line')
        res = super(procurement_order, self).make_po(cr, uid, ids, context=context)
        procurment_id = list(res.keys())
        virtual_file_list = []
        art_wrok_image_list = []
        line_vals = {}
        
        for procurement in self.browse(cr, uid, procurment_id, context=context):
            regex = re.compile("(\W|^)SO[0-9]+:(\W|)MO[0-9]+")
            r = regex.search(procurement.origin or '')
            if procurement and procurement.sale_line_id and r == None:
                data = po_line_obj.browse(cr, uid, res[procurement.id], context=context)
                for art_work_line in procurement.sale_line_id.order_line_image_ids:
                    art_wrok_image_list.append(art_work_line.id)
                line_vals['art_approval_file_ids'] = [(6, 0, art_wrok_image_list)]
                #po_line_obj.write(cr, uid,[data.id], {'art_approval_file_ids':[(6, 0, art_wrok_image_list)] }, context=context)
                virtual_file = self.pool.get("virtual.file")
                for virtual_file in procurement.sale_line_id.virtual_file_ids:
                    virtual_file_list.append(virtual_file.id)
                    virtual_file.write({'purchase_line_id': data.id })
                line_vals['virtual_file_ids'] = [(6, 0, virtual_file_list)]
                po_line_obj.write(cr, uid,[data.id], line_vals, context=context)
        return res

    @api.v7
    def make_mo(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        res = super(procurement_order, self).make_mo(cr, uid, ids, context=context)
        sale_order_line_obj = self.pool.get('sale.order.line')
        mrp_production_obj = self.pool.get('mrp.production')
        procurement_ids = res.keys()
        
        for procurement in self.browse(cr, uid, procurement_ids, context=context):
            if procurement and procurement.sale_line_id :
                vals = {'sub_origin': procurement.sale_line_id.sol_seq }
                mrp_id = res.get(procurement.id)
                virtual_file_list = []
                art_wrok_image_list = []
                for art_work_line in procurement.sale_line_id.order_line_image_ids:
                    art_wrok_image_list.append(art_work_line.id)
                for virtual_file in procurement.sale_line_id.virtual_file_ids:
                    virtual_file_list.append(virtual_file.id)
                if virtual_file_list:
                    vals.update({'virtual_file_ids': [(6, 0, virtual_file_list)]})
                if art_wrok_image_list:
                    vals.update({'art_approval_file_ids':[(6, 0, art_wrok_image_list)]})
                mrp_production_obj.write(cr, uid, [mrp_id], vals, context=context)
        return res