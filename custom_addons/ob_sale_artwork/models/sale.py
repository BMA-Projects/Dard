# -*- encoding: utf-8 -*-
##############################################################################
#
#    OfficeBeacon Administrative Pvt. Ltd
#    RTL Code
#    Copyright (C) 2012 (http://www.officebeacon.com)
#
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm,Warning
from datetime import datetime
from openerp import SUPERUSER_ID, workflow
import time
import re

class sale_order(models.Model):
    _inherit = 'sale.order'
    
    rush_order = fields.Boolean('Is Rush Order ?')
    confirm_date = fields.Date('Order Confirm On')
    client_po_ref =  fields.Char('Customer PO Number', size=64, copy=False)

    _sql_constraints = [
        ('client_po_ref_unique', 'unique (client_po_ref)', 'You can not enter duplicate Customer PO Number !')
    ]
   
    # @api.v7
    # def onchange_client_po_ref(self, cr, uid, ids, client_po_ref, customer_id, context=None):
    #     context = context or {}
    #     res = {}
    #     if client_po_ref and customer_id:
    #         search_val = self.search(cr, uid, [('partner_id','=',customer_id), ('client_po_ref','=',client_po_ref)], context=context)
    #         if search_val:
    #             warning = {
    #                 'title': _('Warning!'),
    #                 'message' : _("You can not use same 'Customer PO Number' twice.")
    #             }
    #             return {'warning': warning}
        # In this code use customer po this field can define in ob_sale_artwork_extend module
        # sale_order_obj = self.pool.get('sale.order')
        # sale_order_line_images_obj = self.pool.get('sale.order.line.images')

        # sale_order_data = sale_order_obj.browse(cr, uid, ids, context)
        # image_line_ids = []
        # if len(sale_order_data.order_line) > 0:
        #     for sol in sale_order_data.order_line:
        #         if len(sol.order_line_image_ids) > 0:
        #             for image_line in sol.order_line_image_ids:
        #                 image_line_ids.append(image_line.id)
        # print "\n\n images wline ids==== ",image_line_ids
        # sale_order_line_images_obj.write(cr, uid, image_line_ids, {'customer_po': client_po_ref}, context=context)
        # return res

    @api.v7
    def _prepare_order_line_procurement(self, cr, uid, order, line, group_id=False, context=None):
        result = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, group_id=group_id, context=context)
        result.update({'sub_origin':line.sol_seq})
        return result
    
    @api.v7
    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        data = self.browse(cr, uid, ids, context=context)
        if data.client_order_ref:
            if data.client_po_ref:
                default.update({
                                'client_po_ref': data.client_po_ref + '(copy)',
                                'date_confirm': False,
                })
        return super(sale_order, self).copy(cr, uid, ids, default, context=context)
    
    @api.v7
    def action_button_confirm(self, cr, uid, ids, context=None):
        order_obj = self.pool.get("sale.order").browse(cr, uid, ids)
        order_line_obj = self.pool.get("sale.order.line")
        order_line_ids = order_line_obj.search(cr, uid, [('order_id','in',ids)], context=context)
        for order_line in order_line_obj.browse(cr, uid, order_line_ids, context=context):
            if order_line.virtual_proofing_required and order_line.manual_approval:
                if not order_line.order_line_image_ids:
                    raise Warning(_('As Artwork Approval is required for some Order Lines, That need to add Artwork Images for Approval Process.'))
                subApproved = True
                for line_image in order_line.order_line_image_ids:
                    if line_image.state not in ['confirmed','semi_confirmed'] :
                        subApproved = False
                if not subApproved and order_line.order_line_image_ids:
                    raise  Warning(_('As Artwork Approval is required for some Order Lines, All Artwork files should be sent and Customer Approved.'))
        self.write(cr, uid, ids, {'confirm_date':time.strftime('%Y-%m-%d')}, context=context)
        return super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

    # def client_po_ref_warning(self):
    #     raise Warning(_('Please, Enter Customer PO Number!'))
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    needed_by = fields.Datetime(string="Needed By")
    size = fields.Char(string="Size")
    virtual_proofing_required = fields.Boolean('Art Proofing Required',copy=True)
    manual_approval = fields.Boolean('Manual Approval' , copy=True)
    order_line_image_ids = fields.One2many('sale.order.line.images', 'order_line_id', 'Upload Files', copy=True)
    virtual_file_ids = fields.One2many('virtual.file', 'line_id', 'Virtual Files', copy=True)
    sol_seq = fields.Char('Order Line #',size=16)
    
    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].get('sale.order.line') or '/'
        values.update({'sol_seq': seq})
        return super(SaleOrderLine, self).create(values)

class mrp_production(models.Model):
    _inherit = 'mrp.production'
    
    sub_origin = fields.Char("Sub Source Document",size=32)
    virtual_file_ids = fields.One2many('virtual.file', 'mrp_id', 'Virtual File')
    art_approval_file_ids = fields.One2many('sale.order.line.images','mrp_id','Art Approval File')
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
